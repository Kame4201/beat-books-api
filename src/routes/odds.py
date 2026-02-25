"""Odds endpoints — delegates to beat-books-data service."""

from typing import List
from fastapi import APIRouter, Query
from pydantic import BaseModel
from src.core.client import data_client

router = APIRouter()


# Response Models
class OddsLine(BaseModel):
    """A single odds line from a sportsbook."""

    game_id: str
    book: str
    home_team: str
    away_team: str
    spread: float
    total: float
    home_moneyline: int
    away_moneyline: int
    timestamp: str


class LiveOddsResponse(BaseModel):
    """Response for live odds across all upcoming games."""

    data: List[OddsLine]


class OddsHistoryResponse(BaseModel):
    """Response for odds movement history on a single game."""

    game_id: str
    history: List[OddsLine]


class BestOddsResponse(BaseModel):
    """Response for best available line across books."""

    data: List[OddsLine]


@router.get("/live", response_model=LiveOddsResponse)
async def get_live_odds(
    sport: str = Query("nfl", description="Sport league"),
):
    """Get current live odds for upcoming games. Delegates to beat-books-data."""
    result = await data_client.get("/odds/live", params={"sport": sport})
    return result


@router.get("/history/{game_id}", response_model=OddsHistoryResponse)
async def get_odds_history(game_id: str):
    """Get odds movement history for a specific game. Delegates to beat-books-data."""
    result = await data_client.get(f"/odds/history/{game_id}")
    return result


@router.get("/best", response_model=BestOddsResponse)
async def get_best_odds(
    sport: str = Query("nfl", description="Sport league"),
):
    """Get best available line across all books. Delegates to beat-books-data."""
    result = await data_client.get("/odds/best", params={"sport": sport})
    return result
