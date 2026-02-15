from fastapi import APIRouter

router = APIRouter()

# TODO: Wire these to beat-books-model service (Phase 2)


@router.get("/predict")
def predict_game(team1: str, team2: str):
    """Predict game outcome. Delegates to beat-books-model."""
    return {"message": f"{team1} vs {team2} prediction — not yet wired to beat-books-model"}
