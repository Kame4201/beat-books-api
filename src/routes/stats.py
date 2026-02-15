from fastapi import APIRouter, Query

router = APIRouter()

# TODO: Wire these to beat-books-data retrieval service


@router.get("/teams/{team}/stats")
def get_team_stats(team: str, season: int = Query(..., ge=1920, le=2100)):
    """Get team statistics. Delegates to beat-books-data."""
    # TODO: Call beat-books-data stats retrieval service
    return {"message": f"Stats for {team} season {season} — not yet wired"}


@router.get("/players")
def get_players(
    season: int = Query(..., ge=1920, le=2100),
    position: str = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=200),
):
    """Get player statistics with filtering. Delegates to beat-books-data."""
    # TODO: Call beat-books-data stats retrieval service
    return {"message": "Player stats — not yet wired"}


@router.get("/games")
def get_games(
    season: int = Query(..., ge=1920, le=2100),
    week: int = Query(None, ge=1, le=22),
):
    """Get game results. Delegates to beat-books-data."""
    # TODO: Call beat-books-data stats retrieval service
    return {"message": "Games — not yet wired"}


@router.get("/standings")
def get_standings(season: int = Query(..., ge=1920, le=2100)):
    """Get season standings. Delegates to beat-books-data."""
    # TODO: Call beat-books-data stats retrieval service
    return {"message": "Standings — not yet wired"}
