"""Career Prediction API routes: POST /api/career/predict and GET /api/career/recommendations."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.career import CareerPredictionResponse, CareerPredictRequest
from app.services.career_service import (
    get_latest_career_recommendations,
    run_career_prediction,
)

router = APIRouter(prefix="/career", tags=["Career Prediction"])


@router.post(
    "/predict",
    response_model=CareerPredictionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Predict top 5 suitable career roles using ML classifier, MiniLM cosine similarity, and Skill Gap Engine",
)
def predict_career(
    payload: CareerPredictRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CareerPredictionResponse:
    return run_career_prediction(payload=payload, current_user=current_user, db=db)


@router.get(
    "/recommendations",
    response_model=CareerPredictionResponse,
    summary="Retrieve the latest persisted top 5 career recommendations for the authenticated user",
)
def get_career_recommendations(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> CareerPredictionResponse:
    return get_latest_career_recommendations(current_user=current_user, db=db)
