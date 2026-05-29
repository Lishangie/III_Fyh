"""Training module for the Credit Risk Scoring service.

Trains multiple classification models on the German Credit Risk dataset,
evaluates them, and saves the best model along with the preprocessor.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier

from src.config import ARTIFACTS_DIR, load_config
from src.data.loader import load_german_credit, save_data
from src.data.preprocessing import CreditPreprocessor

logger = logging.getLogger(__name__)


def train_models() -> None:
    """Main training pipeline.

    1. Loads the German Credit Risk dataset from OpenML.
    2. Preprocesses features using CreditPreprocessor.
    3. Splits data into train/val/test (70/15/15) with stratification.
    4. Trains 5 different classification models.
    5. Evaluates each model on the test set.
    6. Prints a comparison table.
    7. Saves the best model (by ROC-AUC), preprocessor, and results.
    """
    config = load_config()

    # Ensure artifacts directory exists
    ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)

    # ---- Step 1: Load data ----
    logger.info("=" * 60)
    logger.info("Starting model training pipeline")
    logger.info("=" * 60)

    df = load_german_credit()
    logger.info(f"Full dataset shape: {df.shape}")

    # Save raw data
    save_data(df, str(ARTIFACTS_DIR / "raw_data.csv"))

    # ---- Step 2: Preprocess ----
    X = df.drop(columns=["class"])
    y = df["class"]

    preprocessor = CreditPreprocessor()
    X_processed = preprocessor.fit_transform(X)

    logger.info(f"Processed feature matrix shape: {X_processed.shape}")
    logger.info(f"Feature names: {preprocessor.get_feature_names()}")

    # ---- Step 3: Split data ----
    # First split: 70% train, 30% temp (val + test)
    X_train, X_temp, y_train, y_temp = train_test_split(
        X_processed,
        y.values,
        test_size=0.30,
        random_state=config.model.random_state,
        stratify=y.values,
    )

    # Second split: 50% of temp for val, 50% for test -> 15% each overall
    X_val, X_test, y_val, y_test = train_test_split(
        X_temp,
        y_temp,
        test_size=0.50,
        random_state=config.model.random_state,
        stratify=y_temp,
    )

    logger.info(f"Train set: {X_train.shape[0]} samples")
    logger.info(f"Validation set: {X_val.shape[0]} samples")
    logger.info(f"Test set: {X_test.shape[0]} samples")

    # ---- Step 4: Define models ----
    models: Dict[str, object] = {
        "LogisticRegression": LogisticRegression(
            max_iter=1000,
            random_state=config.model.random_state,
        ),
        "DecisionTreeClassifier": DecisionTreeClassifier(
            random_state=config.model.random_state,
        ),
        "RandomForestClassifier": RandomForestClassifier(
            n_estimators=200,
            max_depth=10,
            random_state=config.model.random_state,
            n_jobs=-1,
        ),
        "GradientBoostingClassifier": GradientBoostingClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=config.model.random_state,
        ),
        "MLPClassifier": MLPClassifier(
            hidden_layer_sizes=(64, 32),
            max_iter=500,
            early_stopping=True,
            random_state=config.model.random_state,
        ),
    }

    # ---- Step 5: Train and evaluate ----
    results: List[Dict] = []
    best_auc: float = -1.0
    best_model_name: str = ""
    best_model = None

    for name, model in models.items():
        logger.info(f"\nTraining {name}...")

        model.fit(X_train, y_train)

        # Predict on test set
        y_pred = model.predict(X_test)

        # Get probability estimates for ROC-AUC
        if hasattr(model, "predict_proba"):
            y_proba = model.predict_proba(X_test)[:, 1]
        elif hasattr(model, "decision_function"):
            y_proba = model.decision_function(X_test)
        else:
            y_proba = y_pred.astype(float)

        # Calculate metrics
        auc = roc_auc_score(y_test, y_proba)
        f1 = f1_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred)
        recall = recall_score(y_test, y_pred)

        result = {
            "model_name": name,
            "roc_auc": round(auc, 4),
            "f1_score": round(f1, 4),
            "precision": round(precision, 4),
            "recall": round(recall, 4),
        }
        results.append(result)

        logger.info(
            f"  ROC-AUC: {auc:.4f} | F1: {f1:.4f} | "
            f"Precision: {precision:.4f} | Recall: {recall:.4f}"
        )

        # Track best model by ROC-AUC
        if auc > best_auc:
            best_auc = auc
            best_model_name = name
            best_model = model

    # ---- Step 6: Print comparison table ----
    print("\n" + "=" * 75)
    print("MODEL COMPARISON RESULTS")
    print("=" * 75)
    header = f"{'Model':<30} {'ROC-AUC':>10} {'F1':>10} {'Precision':>10} {'Recall':>10}"
    print(header)
    print("-" * 75)
    for r in results:
        row = (
            f"{r['model_name']:<30} "
            f"{r['roc_auc']:>10.4f} "
            f"{r['f1_score']:>10.4f} "
            f"{r['precision']:>10.4f} "
            f"{r['recall']:>10.4f}"
        )
        print(row)
    print("=" * 75)
    print(f"Best model: {best_model_name} (ROC-AUC: {best_auc:.4f})")
    print()

    # ---- Step 7: Save artifacts ----
    # Save best model
    model_path = ARTIFACTS_DIR / "model.pkl"
    joblib.dump(best_model, model_path)
    logger.info(f"Best model ({best_model_name}) saved to {model_path}")

    # Save preprocessor
    preprocessor_path = ARTIFACTS_DIR / "preprocessor.pkl"
    preprocessor.save(str(preprocessor_path))

    # Save comparison results
    results_data = {
        "best_model": best_model_name,
        "best_roc_auc": round(best_auc, 4),
        "all_results": results,
        "config": {
            "random_state": config.model.random_state,
            "test_size": config.model.test_size,
            "val_size": config.model.val_size,
        },
    }
    results_path = ARTIFACTS_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(results_data, f, indent=2)
    logger.info(f"Results saved to {results_path}")

    logger.info("=" * 60)
    logger.info("Training pipeline completed successfully!")
    logger.info("=" * 60)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    train_models()
