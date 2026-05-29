"""Prediction module for the Credit Risk Scoring service.

Provides the CreditScoringModel class that loads a trained model and
preprocessor, and makes credit risk predictions on new data.
"""

import logging
from typing import Any, Dict, Optional

import joblib
import numpy as np
import pandas as pd

from src.config import ARTIFACTS_DIR, load_config
from src.data.preprocessing import CATEGORICAL_FEATURES, NUMERICAL_FEATURES, CreditPreprocessor

logger = logging.getLogger(__name__)


class CreditScoringModel:
    """Credit risk scoring model for prediction.

    Loads a trained model and fitted preprocessor from artifacts,
    then provides prediction functionality with probability-based
    risk categorization.

    Attributes:
        model: The trained scikit-learn model.
        preprocessor: The fitted CreditPreprocessor.
        model_name: Name/class of the loaded model.
        config: Application configuration.
    """

    def __init__(
        self,
        model_path: Optional[str] = None,
        preprocessor_path: Optional[str] = None,
    ) -> None:
        """Initialize the scoring model by loading artifacts.

        Args:
            model_path: Path to the saved model pickle file.
                Defaults to artifacts/model.pkl.
            preprocessor_path: Path to the saved preprocessor pickle file.
                Defaults to artifacts/preprocessor.pkl.
        """
        self.config = load_config()

        if model_path is None:
            model_path = str(ARTIFACTS_DIR / "model.pkl")
        if preprocessor_path is None:
            preprocessor_path = str(ARTIFACTS_DIR / "preprocessor.pkl")

        self.model = joblib.load(model_path)
        logger.info(f"Model loaded from {model_path}")

        self.preprocessor = CreditPreprocessor.load(preprocessor_path)
        logger.info(f"Preprocessor loaded from {preprocessor_path}")

        self.model_name = type(self.model).__name__
        logger.info(f"Model type: {self.model_name}")

    def predict(self, features_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Predict the probability of loan default for a credit application.

        Takes a dictionary of feature names to values, preprocesses the data,
        and returns the default probability with a risk category.

        Args:
            features_dict: Dictionary mapping feature names to values.
                Must contain all 20 features expected by the model.

        Returns:
            Dictionary with:
                - default_probability (float): Probability of default (0.0 to 1.0).
                - risk_category (str): 'low', 'medium', or 'high'.
                - model_name (str): Name of the model used.

        Raises:
            ValueError: If required features are missing.
        """
        # Build DataFrame from input dict
        df = pd.DataFrame([features_dict])

        # Verify all expected features are present
        expected_features = CATEGORICAL_FEATURES + NUMERICAL_FEATURES
        missing_features = set(expected_features) - set(df.columns)
        if missing_features:
            raise ValueError(
                f"Missing features in input: {missing_features}. "
                f"Required features: {expected_features}"
            )

        # Ensure columns are in the right order
        df = df[expected_features]

        # Preprocess
        X = self.preprocessor.transform(df)

        # Predict probability of default (class 0 = bad/default)
        if hasattr(self.model, "predict_proba"):
            proba = self.model.predict_proba(X)[0]
            # predict_proba returns [P(class_0), P(class_1)]
            # class 0 = bad/default, so default_probability = P(class_0)
            default_probability = float(proba[0])
        elif hasattr(self.model, "decision_function"):
            decision = float(self.model.decision_function(X)[0])
            # Convert decision function to probability using sigmoid
            default_probability = 1.0 / (1.0 + np.exp(decision))
        else:
            # Fallback: use raw prediction
            prediction = self.model.predict(X)[0]
            default_probability = float(1 - prediction)  # if predicted good (1), low default prob

        # Clamp to [0, 1]
        default_probability = max(0.0, min(1.0, default_probability))

        # Determine risk category
        risk_category = self._determine_risk_category(default_probability)

        result = {
            "default_probability": round(default_probability, 4),
            "risk_category": risk_category,
            "model_name": self.model_name,
        }

        logger.info(
            f"Prediction: default_probability={result['default_probability']:.4f}, "
            f"risk_category={risk_category}, model={self.model_name}"
        )

        return result

    def _determine_risk_category(self, probability: float) -> str:
        """Determine risk category based on default probability.

        Thresholds:
            - low: probability < 0.3
            - medium: 0.3 <= probability < 0.6
            - high: probability >= 0.6

        Args:
            probability: Default probability (0.0 to 1.0).

        Returns:
            Risk category string: 'low', 'medium', or 'high'.
        """
        low_threshold = self.config.risk_thresholds.low
        high_threshold = self.config.risk_thresholds.high

        if probability < low_threshold:
            return "low"
        elif probability < high_threshold:
            return "medium"
        else:
            return "high"

    def health_check(self) -> bool:
        """Check if the model is loaded and ready for predictions.

        Returns:
            True if model and preprocessor are loaded, False otherwise.
        """
        try:
            return (
                self.model is not None
                and self.preprocessor is not None
                and self.preprocessor._is_fitted
            )
        except Exception:
            return False
