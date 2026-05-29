"""Unit tests for model training and prediction."""

import json
import pytest
import numpy as np
import joblib
from pathlib import Path

from src.config import ARTIFACTS_DIR
from src.data.loader import load_german_credit
from src.data.preprocessing import CreditPreprocessor
from src.models.predict import CreditScoringModel


# Use the already-trained model in artifacts/
ARTIFACTS_PATH = ARTIFACTS_DIR


@pytest.fixture(scope="module")
def scoring_model():
    """Create a CreditScoringModel from the existing trained artifacts."""
    model_path = str(ARTIFACTS_PATH / "model.pkl")
    preprocessor_path = str(ARTIFACTS_PATH / "preprocessor.pkl")
    return CreditScoringModel(
        model_path=model_path,
        preprocessor_path=preprocessor_path,
    )


@pytest.fixture
def sample_features():
    """Sample feature dictionary for testing."""
    return {
        "checking_account": "A11",
        "duration": 12,
        "credit_history": "A32",
        "purpose": "A43",
        "credit_amount": 2000,
        "savings_account": "A61",
        "employment_since": "A73",
        "installment_rate": 2,
        "personal_status": "A93",
        "other_debtors": "A101",
        "residence_since": 2,
        "property": "A123",
        "age": 30,
        "other_installment_plans": "A143",
        "housing": "A152",
        "existing_credits": 1,
        "job": "A173",
        "people_liable": 1,
        "telephone": "A192",
        "foreign_worker": "A201",
    }


class TestTrainArtifacts:
    """Tests that training artifacts exist and are valid."""

    def test_model_file_exists(self):
        """Verify model file exists in artifacts."""
        model_path = ARTIFACTS_PATH / "model.pkl"
        assert model_path.exists(), f"Model file should exist at {model_path}"

    def test_preprocessor_file_exists(self):
        """Verify preprocessor file exists in artifacts."""
        preprocessor_path = ARTIFACTS_PATH / "preprocessor.pkl"
        assert preprocessor_path.exists(), f"Preprocessor file should exist at {preprocessor_path}"

    def test_results_file_exists(self):
        """Verify results file exists in artifacts."""
        results_path = ARTIFACTS_PATH / "results.json"
        assert results_path.exists(), f"Results file should exist at {results_path}"

    def test_results_structure(self):
        """Verify results file has correct structure."""
        results_path = ARTIFACTS_PATH / "results.json"
        with open(results_path, "r") as f:
            results = json.load(f)

        assert "best_model" in results, "Results should contain best_model"
        assert "best_roc_auc" in results, "Results should contain best_roc_auc"
        assert "all_results" in results, "Results should contain all_results"
        assert len(results["all_results"]) == 5, "Should have results for 5 models"

    def test_best_model_roc_auc_above_baseline(self):
        """Verify the best model achieves ROC-AUC above 0.5 (random)."""
        results_path = ARTIFACTS_PATH / "results.json"
        with open(results_path, "r") as f:
            results = json.load(f)

        assert results["best_roc_auc"] > 0.5, (
            f"Best ROC-AUC {results['best_roc_auc']} should be above 0.5 (random)"
        )


class TestCreditScoringModel:
    """Tests for the prediction model."""

    def test_predict_model(self, scoring_model, sample_features):
        """Test prediction with sample features."""
        result = scoring_model.predict(sample_features)

        assert "default_probability" in result, "Result should contain default_probability"
        assert "risk_category" in result, "Result should contain risk_category"
        assert "model_name" in result, "Result should contain model_name"

        assert 0.0 <= result["default_probability"] <= 1.0, (
            "Default probability should be between 0 and 1"
        )

    def test_risk_category_low(self, scoring_model):
        """Test risk categorization for low probability."""
        result = scoring_model._determine_risk_category(0.1)
        assert result == "low", f"Probability 0.1 should be 'low', got '{result}'"

    def test_risk_category_medium(self, scoring_model):
        """Test risk categorization for medium probability."""
        result = scoring_model._determine_risk_category(0.45)
        assert result == "medium", f"Probability 0.45 should be 'medium', got '{result}'"

    def test_risk_category_high(self, scoring_model):
        """Test risk categorization for high probability."""
        result = scoring_model._determine_risk_category(0.8)
        assert result == "high", f"Probability 0.8 should be 'high', got '{result}'"

    def test_health_check(self, scoring_model):
        """Test model health check."""
        is_healthy = scoring_model.health_check()
        assert is_healthy is True, "Health check should return True for loaded model"

    def test_predict_missing_features_raises(self, scoring_model):
        """Test prediction with missing features raises ValueError."""
        incomplete_features = {
            "duration": 12,
            "credit_amount": 2000,
        }
        with pytest.raises(ValueError, match="Missing features"):
            scoring_model.predict(incomplete_features)
