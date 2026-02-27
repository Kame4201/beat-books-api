from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from typing import Optional, List, Literal
import httpx
from src.core.config import settings

router = APIRouter()

# Valid NFL team abbreviations (32 teams)
VALID_NFL_TEAMS = {
    "cardinals",
    "falcons",
    "ravens",
    "bills",
    "panthers",
    "bears",
    "bengals",
    "browns",
    "cowboys",
    "broncos",
    "lions",
    "packers",
    "texans",
    "colts",
    "jaguars",
    "chiefs",
    "raiders",
    "chargers",
    "rams",
    "dolphins",
    "vikings",
    "patriots",
    "saints",
    "giants",
    "jets",
    "eagles",
    "steelers",
    "49ers",
    "seahawks",
    "buccaneers",
    "titans",
    "commanders",
}


# Response Models
class PredictionResponse(BaseModel):
    """Response model for game prediction."""

    home_team: str
    away_team: str
    home_win_probability: float = Field(..., ge=0.0, le=1.0)
    away_win_probability: float = Field(..., ge=0.0, le=1.0)
    predicted_spread: float
    model_version: str
    feature_version: str
    edge_vs_market: float
    recommended_bet_size: float = Field(..., ge=0.0, le=1.0)
    bet_recommendation: Literal["BET", "NO_BET"]


class BacktestResponse(BaseModel):
    """Response model for backtest results."""

    run_id: str
    start_date: str
    end_date: str
    total_games: int
    correct_predictions: int
    accuracy: float = Field(..., ge=0.0, le=1.0)
    total_profit: float
    roi: float
    sharpe_ratio: Optional[float] = None


class ModelInfo(BaseModel):
    """Response model for model information."""

    model_id: str
    model_version: str
    feature_version: str
    trained_date: str
    accuracy: float = Field(..., ge=0.0, le=1.0)
    is_active: bool


class ModelsListResponse(BaseModel):
    """Response model for list of models."""

    models: List[ModelInfo]


def validate_team_name(team: str) -> str:
    """Validate and normalize NFL team name."""
    normalized = team.lower().strip()
    if normalized not in VALID_NFL_TEAMS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid team name: '{team}'. Must be a valid NFL team abbreviation (e.g., chiefs, eagles, patriots).",
        )
    return normalized


@router.get("/predict")
async def predict_game(
    team1: str = Query(..., description="Home team name (NFL team abbreviation)"),
    team2: str = Query(..., description="Away team name (NFL team abbreviation)"),
):
    """
    Predict game outcome between two teams.

    Delegates to beat-books-model service for prediction computation.

    Args:
        team1: Home team name (NFL abbreviation, e.g., 'chiefs')
        team2: Away team name (NFL abbreviation, e.g., 'eagles')

    Returns:
        PredictionResponse with probabilities, spread, and betting recommendation

    Raises:
        HTTPException: 400 if team names are invalid
        HTTPException: 503 if model service is unavailable
    """
    # Validate team names
    home_team = validate_team_name(team1)
    away_team = validate_team_name(team2)

    # Delegate to beat-books-model service (POST /predictions/predict)
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.MODEL_SERVICE_URL}/predictions/predict",
                json={"home_team": home_team, "away_team": away_team},
                timeout=10.0,
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Model service unavailable. Please ensure beat-books-model is running.",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Model service error: {e.response.text}",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, detail="Model service timeout. Request took too long."
        )


@router.get("/backtest/{run_id}", response_model=BacktestResponse)
async def get_backtest_results(run_id: str):
    """
    Retrieve backtest results by run ID.

    Delegates to beat-books-model service to fetch backtest results.

    Args:
        run_id: Unique identifier for the backtest run

    Returns:
        BacktestResponse with accuracy, profit, ROI, and other metrics

    Raises:
        HTTPException: 404 if backtest run not found
        HTTPException: 503 if model service is unavailable
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.MODEL_SERVICE_URL}/backtest/{run_id}", timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Model service unavailable. Please ensure beat-books-model is running.",
        )
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            raise HTTPException(
                status_code=404, detail=f"Backtest run '{run_id}' not found."
            )
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Model service error: {e.response.text}",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, detail="Model service timeout. Request took too long."
        )


@router.get("/models", response_model=ModelsListResponse)
async def list_models():
    """
    List all available trained models.

    Delegates to beat-books-model service to retrieve model metadata.

    Returns:
        ModelsListResponse with list of available models and their metadata

    Raises:
        HTTPException: 503 if model service is unavailable
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.MODEL_SERVICE_URL}/models", timeout=10.0
            )
            response.raise_for_status()
            return response.json()
    except httpx.ConnectError:
        raise HTTPException(
            status_code=503,
            detail="Model service unavailable. Please ensure beat-books-model is running.",
        )
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Model service error: {e.response.text}",
        )
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504, detail="Model service timeout. Request took too long."
        )
