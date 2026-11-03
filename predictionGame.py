import fastf1
from functools import lru_cache
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

def scorePrediction(prediction, actual):
    score = 0

    for i in range(5):
        if prediction[i] == actual[i]:
            score += 3
        elif prediction[i] in actual:
            score += 1

    if prediction == actual:
        score += 5

    return score

@lru_cache(maxsize=64)
def getActualTop5(year, race, session_type):
    session = fastf1.get_session(year, race, session_type)
    session.load(telemetry=False, weather=False, messages=False)

    return (
        session.results
        .sort_values("Position")
        .head(5)["Abbreviation"]
        .tolist()
    )

def comparePredictions(user_prediction, ai_prediction, actual):
    user_score = scorePrediction(user_prediction, actual)
    ai_score = scorePrediction(ai_prediction, actual)

    if user_score > ai_score:
        winner = "User"
    elif ai_score > user_score:
        winner = "AI"
    else:
        winner = "Draw"

    return user_score, ai_score, winner

class PredictionRequest(BaseModel):
    year: int
    race: str
    session_type: str = "R"
    user_prediction: list[str]
    ai_prediction: list[str]

@router.post("/prediction-score")
def predictionAPI(request: PredictionRequest):
    actual = getActualTop5(
        request.year,
        request.race,
        request.session_type
    )

    user_score, ai_score, winner = comparePredictions(
        request.user_prediction,
        request.ai_prediction,
        actual
    )

    return {
        "UserPrediction": request.user_prediction,
        "AIPrediction": request.ai_prediction,
        "Actual": actual,
        "UserScore": user_score,
        "AIScore": ai_score,
        "Winner": winner
    }

if __name__ == "__main__":
    user_prediction = ["VER", "NOR", "PIA", "RUS", "LEC"]
    ai_prediction = ["NOR", "PIA", "VER", "LEC", "RUS"]

    actual = getActualTop5(2025, "Qatar", "R")

    user_score, ai_score, winner = comparePredictions(
        user_prediction,
        ai_prediction,
        actual
    )

    print("User:", user_score)
    print("AI:", ai_score)
    print("Winner:", winner)
