"""Train, evaluate, and save the SkillGap AI 12-role ML Career Prediction model."""

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
BACKEND_DIR = PROJECT_ROOT / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.ml.career.model_trainer import train_and_save_career_model  # noqa: E402


def main() -> int:
    print("Training SkillGap AI Career Prediction Engine (12 roles)...")
    result = train_and_save_career_model(samples_per_role=40, test_size=0.2, random_state=42)
    report = result["evaluation_report"]

    print(f"\nSelected Classifier : {result['selected_model_name']}")
    print(f"Dataset Provenance  : {report['dataset_provenance']} (synthetic={report['is_synthetic_dataset']})")
    print(f"Train / Test Split  : {report['train_samples']} / {report['test_samples']}")
    print(f"Accuracy            : {report['accuracy']:.4f}")
    print(f"Precision (macro)   : {report['precision_macro']:.4f}")
    print(f"Recall (macro)      : {report['recall_macro']:.4f}")
    print(f"F1-Score (macro)    : {report['f1_macro']:.4f}")
    print(f"CV F1-Score (5-fold): {report['cv_f1_macro_mean']:.4f} +/- {report['cv_f1_macro_std']:.4f}")
    print("\nClassifier Comparison (Held-Out Test Set):")
    for row in report["model_comparison"]:
        print(
            f"  - {row['model_name']:20s} | Acc={row['accuracy']:.4f} "
            f"| Prec={row['precision_macro']:.4f} | Rec={row['recall_macro']:.4f} "
            f"| F1={row['f1_macro']:.4f} | CV_F1={row['cv_f1_macro_mean']:.4f}"
        )
    print("\nSaved Artifacts:")
    for key, val in result["artifacts"].items():
        print(f"  - {key}: {val}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
