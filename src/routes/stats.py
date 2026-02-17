from typing import Optional
from fastapi import APIRouter, Query
from src.core.client import data_client
from src.core.enums import Position

router = APIRouter()


@router.get("/teams/{team}/stats")
async def get_team_stats(team: str, season: int = Query(..., ge=1920, le=2100)):
    """Get team statistics. Delegates to beat-books-data."""
    result = await data_client.get(f"/stats/teams/{team}", params={"season": season})
    return result


@router.get("/players")
async def get_players(
    season: int = Query(..., ge=1920, le=2100),
    position: Optional[Position] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    """Get player statistics with filtering. Delegates to beat-books-data."""
    params: dict[str, int | str] = {"season": season, "page": page, "limit": limit}
    if position:
        params["position"] = position.value

    result = await data_client.get("/stats/players", params=params)
    return result


@router.get("/games")
async def get_games(
    season: int = Query(..., ge=1920, le=2100),
    week: Optional[int] = Query(None, ge=1, le=22),
):
    """Get game results. Delegates to beat-books-data."""
    params = {"season": season}
    if week is not None:
        params["week"] = week

    result = await data_client.get("/stats/games", params=params)
    return result


@router.get("/standings")
async def get_standings(season: int = Query(..., ge=1920, le=2100)):
    """Get season standings. Delegates to beat-books-data."""
    result = await data_client.get("/stats/standings", params={"season": season})
    return result
