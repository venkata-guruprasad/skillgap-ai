"""Modular ML Career Prediction Engine package (Phase 6)."""

from app.ml.career.career_recommender import EMPLOYMENT_DISCLAIMER, predict_top_careers
from app.ml.career.dataset_builder import (
    CAREER_ROLE_CATALOG,
    DATASET_PROVENANCE,
    build_synthetic_career_dataset,
)
from app.ml.career.model_evaluator import evaluate_classifier_predictions
from app.ml.career.model_loader import clear_model_cache, load_trained_bundle
from app.ml.career.model_store import save_trained_bundle
from app.ml.career.model_trainer import train_and_save_career_model

__all__ = [
    "CAREER_ROLE_CATALOG",
    "DATASET_PROVENANCE",
    "EMPLOYMENT_DISCLAIMER",
    "build_synthetic_career_dataset",
    "evaluate_classifier_predictions",
    "save_trained_bundle",
    "train_and_save_career_model",
    "load_trained_bundle",
    "clear_model_cache",
    "predict_top_careers",
]
