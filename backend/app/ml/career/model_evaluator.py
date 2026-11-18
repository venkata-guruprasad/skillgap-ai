"""Model evaluation module: Accuracy, Precision, Recall, F1-score, and Confusion Matrix."""

from typing import Any, Dict, List, Sequence

from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)


def evaluate_classifier_predictions(
    y_true: Sequence[str],
    y_pred: Sequence[str],
    labels: Sequence[str],
    model_name: str,
    train_size: int,
    test_size: int,
    is_synthetic_dataset: bool = True,
    dataset_provenance: str = "synthetic_skillgap_career_dataset_v1",
) -> Dict[str, Any]:
    """Compute real held-out evaluation metrics without inventing or inflating scores."""
    ordered_labels = list(labels)

    acc = float(accuracy_score(y_true, y_pred))
    prec_macro = float(precision_score(y_true, y_pred, average="macro", zero_division=0))
    prec_weighted = float(precision_score(y_true, y_pred, average="weighted", zero_division=0))
    rec_macro = float(recall_score(y_true, y_pred, average="macro", zero_division=0))
    rec_weighted = float(recall_score(y_true, y_pred, average="weighted", zero_division=0))
    f1_macro = float(f1_score(y_true, y_pred, average="macro", zero_division=0))
    f1_weighted = float(f1_score(y_true, y_pred, average="weighted", zero_division=0))

    cm = confusion_matrix(y_true, y_pred, labels=ordered_labels).tolist()
    report_dict = classification_report(
        y_true,
        y_pred,
        labels=ordered_labels,
        output_dict=True,
        zero_division=0,
    )

    per_class: List[Dict[str, Any]] = []
    for label in ordered_labels:
        entry = report_dict.get(label, {})
        per_class.append(
            {
                "role": label,
                "precision": round(float(entry.get("precision", 0.0)), 4),
                "recall": round(float(entry.get("recall", 0.0)), 4),
                "f1_score": round(float(entry.get("f1-score", 0.0)), 4),
                "support": int(entry.get("support", 0)),
            }
        )

    return {
        "model_name": model_name,
        "dataset_provenance": dataset_provenance,
        "is_synthetic_dataset": is_synthetic_dataset,
        "evaluation_notice": (
            "Evaluated on a held-out 20% test split of a clearly labeled synthetic "
            "career dataset (no train/test leakage). These metrics measure synthetic "
            "benchmark performance and must not be interpreted as real-world hiring accuracy."
            if is_synthetic_dataset
            else "Evaluated on a held-out 20% test split."
        ),
        "train_samples": train_size,
        "test_samples": test_size,
        "accuracy": round(acc, 4),
        "precision_macro": round(prec_macro, 4),
        "precision_weighted": round(prec_weighted, 4),
        "recall_macro": round(rec_macro, 4),
        "recall_weighted": round(rec_weighted, 4),
        "f1_macro": round(f1_macro, 4),
        "f1_weighted": round(f1_weighted, 4),
        "labels": ordered_labels,
        "confusion_matrix": cm,
        "per_class_metrics": per_class,
    }
