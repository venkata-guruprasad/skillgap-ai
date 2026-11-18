"""Model training module: leak-free train/test split, TF-IDF pipelines, and MiniLM role prototypes."""

from datetime import datetime, timezone
from typing import Any, Dict, List

import numpy as np
from sklearn.calibration import CalibratedClassifierCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.svm import LinearSVC

from app.ml.career.dataset_builder import (
    CAREER_ROLE_CATALOG,
    DATASET_PROVENANCE,
    build_synthetic_career_dataset,
)
from app.ml.career.model_evaluator import evaluate_classifier_predictions
from app.ml.career.model_store import save_trained_bundle
from app.ml.semantic_matcher import load_embedding_model


def _build_candidate_pipelines(random_state: int = 42) -> Dict[str, Pipeline]:
    """Define Scikit-learn TF-IDF + Classification pipelines fitted ONLY on training folds."""
    return {
        "LogisticRegression": Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        sublinear_tf=True,
                        min_df=2,
                        max_features=4000,
                        stop_words="english",
                    ),
                ),
                (
                    "clf",
                    LogisticRegression(
                        C=2.0,
                        max_iter=1000,
                        random_state=random_state,
                    ),
                ),
            ]
        ),
        "CalibratedLinearSVC": Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        sublinear_tf=True,
                        min_df=2,
                        max_features=4000,
                        stop_words="english",
                    ),
                ),
                (
                    "clf",
                    CalibratedClassifierCV(
                        LinearSVC(C=1.0, random_state=random_state),
                        cv=3,
                        method="sigmoid",
                    ),
                ),
            ]
        ),
        "RandomForest": Pipeline(
            [
                (
                    "tfidf",
                    TfidfVectorizer(
                        ngram_range=(1, 2),
                        sublinear_tf=True,
                        min_df=2,
                        max_features=3000,
                        stop_words="english",
                    ),
                ),
                (
                    "clf",
                    RandomForestClassifier(
                        n_estimators=180,
                        max_depth=18,
                        random_state=random_state,
                        n_jobs=-1,
                    ),
                ),
            ]
        ),
    }


def _compute_role_prototype_embeddings(
    catalog: List[Dict[str, Any]],
) -> Dict[str, Any]:
    """Precompute normalized Sentence Transformer role embeddings for cosine similarity."""
    model, model_name = load_embedding_model()
    role_texts = [
        (
            f"{role['title']} ({role['category']}). "
            f"Required skills: {', '.join(s['name'] for s in role['required_skills'])}. "
            f"Preferred skills: {', '.join(s['name'] for s in role['preferred_skills'])}. "
            f"{role['role_description']}"
        )
        for role in catalog
    ]

    if model is None:
        return {"semantic_model": model_name, "embeddings": None, "role_texts": role_texts}

    matrix = model.encode(role_texts, normalize_embeddings=True, show_progress_bar=False)
    embeddings = {
        role["title"]: np.asarray(matrix[idx], dtype=np.float32).tolist()
        for idx, role in enumerate(catalog)
    }
    return {"semantic_model": model_name, "embeddings": embeddings, "role_texts": role_texts}


def train_and_save_career_model(
    samples_per_role: int = 40,
    test_size: float = 0.2,
    random_state: int = 42,
    save_artifacts: bool = True,
) -> Dict[str, Any]:
    """Prepare dataset, split cleanly (no leakage), train/compare classifiers, evaluate, and save."""
    rows = build_synthetic_career_dataset(
        samples_per_role=samples_per_role,
        seed=random_state,
        save_to_disk=save_artifacts,
    )

    texts = [r["profile_text"] for r in rows]
    labels_y = [r["career_role"] for r in rows]
    ordered_roles = [r["title"] for r in CAREER_ROLE_CATALOG]

    # Strictly split BEFORE vectorization or training to prevent any data leakage
    X_train, X_test, y_train, y_test = train_test_split(
        texts,
        labels_y,
        test_size=test_size,
        random_state=random_state,
        stratify=labels_y,
    )

    pipelines = _build_candidate_pipelines(random_state=random_state)
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=random_state)

    comparison: List[Dict[str, Any]] = []
    best_name = ""
    best_pipeline = None
    best_eval: Dict[str, Any] = {}
    best_f1 = -1.0

    for name, pipeline in pipelines.items():
        # 5-fold CV strictly inside X_train only
        cv_scores = cross_val_score(pipeline, X_train, y_train, cv=cv, scoring="f1_macro")
        pipeline.fit(X_train, y_train)
        y_pred = pipeline.predict(X_test)

        eval_report = evaluate_classifier_predictions(
            y_true=y_test,
            y_pred=y_pred,
            labels=ordered_roles,
            model_name=name,
            train_size=len(X_train),
            test_size=len(X_test),
            is_synthetic_dataset=True,
            dataset_provenance=DATASET_PROVENANCE,
        )
        eval_report["cv_f1_macro_mean"] = round(float(np.mean(cv_scores)), 4)
        eval_report["cv_f1_macro_std"] = round(float(np.std(cv_scores)), 4)

        comparison.append(
            {
                "model_name": name,
                "accuracy": eval_report["accuracy"],
                "precision_macro": eval_report["precision_macro"],
                "recall_macro": eval_report["recall_macro"],
                "f1_macro": eval_report["f1_macro"],
                "cv_f1_macro_mean": eval_report["cv_f1_macro_mean"],
            }
        )

        if eval_report["f1_macro"] > best_f1:
            best_f1 = eval_report["f1_macro"]
            best_name = name
            best_pipeline = pipeline
            best_eval = eval_report

    best_eval["model_comparison"] = comparison
    best_eval["trained_at"] = datetime.now(timezone.utc).isoformat()

    prototypes = _compute_role_prototype_embeddings(CAREER_ROLE_CATALOG)

    bundle = {
        "model_version": "1.0.0",
        "selected_model_name": best_name,
        "pipeline": best_pipeline,
        "classes": list(best_pipeline.classes_),
        "role_catalog": CAREER_ROLE_CATALOG,
        "role_embeddings": prototypes["embeddings"],
        "semantic_model": prototypes["semantic_model"],
        "evaluation_report": best_eval,
        "trained_at": best_eval["trained_at"],
        "is_synthetic_dataset": True,
        "dataset_provenance": DATASET_PROVENANCE,
    }

    paths = {}
    if save_artifacts:
        paths = save_trained_bundle(bundle=bundle, evaluation_report=best_eval)

    return {
        "selected_model_name": best_name,
        "evaluation_report": best_eval,
        "artifacts": paths,
        "bundle": bundle,
    }
