"""Model loading module: loads cached trained career model bundle from disk."""

from functools import lru_cache
import logging
from pathlib import Path
from typing import Any, Dict

import joblib

from app.ml.career.model_store import MODEL_BUNDLE_PATH

logger = logging.getLogger("skillgap_ai.career_loader")


@lru_cache(maxsize=1)
def load_trained_bundle(bundle_path: str = str(MODEL_BUNDLE_PATH)) -> Dict[str, Any]:
    """Load the saved career prediction bundle from disk; auto-trains once if missing."""
    path = Path(bundle_path)
    if not path.exists():
        logger.info("Trained career model bundle not found at %s; running initial training.", path)
        from app.ml.career.model_trainer import train_and_save_career_model

        result = train_and_save_career_model(save_artifacts=True)
        return result["bundle"]

    logger.info("Loading trained career model bundle from %s", path)
    return joblib.load(path)


def clear_model_cache() -> None:
    """Clear in-memory cached model bundle (useful after retraining)."""
    load_trained_bundle.cache_clear()
