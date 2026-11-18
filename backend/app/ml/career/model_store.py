"""Model saving module: persists trained career classification artifacts and evaluation report."""

import json
import os
from pathlib import Path
from typing import Any, Dict

import joblib

PROJECT_ROOT = Path(__file__).resolve().parents[4]
TRAINED_MODELS_DIR = Path(
    os.getenv("MODEL_DIR", str(PROJECT_ROOT / "models" / "trained"))
)
MODEL_BUNDLE_PATH = TRAINED_MODELS_DIR / "career_model_bundle.joblib"
EVALUATION_REPORT_PATH = TRAINED_MODELS_DIR / "career_evaluation_report.json"


def save_trained_bundle(
    bundle: Dict[str, Any],
    evaluation_report: Dict[str, Any],
    bundle_path: Path = MODEL_BUNDLE_PATH,
    report_path: Path = EVALUATION_REPORT_PATH,
) -> Dict[str, str]:
    """Persist trained model bundle (joblib) and evaluation metrics (JSON)."""
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)

    joblib.dump(bundle, bundle_path, compress=3)
    with report_path.open("w", encoding="utf-8") as fh:
        json.dump(evaluation_report, fh, indent=2)

    return {
        "bundle_path": str(bundle_path),
        "report_path": str(report_path),
    }
