"""Unit tests for FastAPI service using TestClient."""

import pytest
from fastapi.testclient import TestClient

from src.config import ARTIFACTS_DIR
from src.models.predict import CreditScoringModel
import src.service.app as app_module
from src.service.app import app


@pytest.fixture(scope="module")
def client():
    """Create a TestClient with the trained model loaded."""
    model_path = str(ARTIFACTS_DIR / "model.pkl")
    preprocessor_path = str(ARTIFACTS_DIR / "preprocessor.pkl")

    # Manually load the model
    test_model = CreditScoringModel(
        model_path=model_path,
        preprocessor_path=preprocessor_path,
    )

    # Set the global model in the app module
    app_module._model = test_model

    with TestClient(app) as c:
        yield c

    # Cleanup
    app_module._model = None


@pytest.fixture
def sample_application():
    """Sample credit application data for testing."""
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
        "property_type": "A123",
        "age": 30,
        "other_installment_plans": "A143",
        "housing": "A152",
        "existing_credits": 1,
        "job": "A173",
        "people_liable": 1,
        "telephone": "A192",
        "foreign_worker": "A201",
    }


class TestHealthEndpoint:
    """Tests for the /health endpoint."""

    def test_health_endpoint(self, client):
        """GET /health returns 200 and healthy status."""
        response = client.get("/health")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        data = response.json()
        assert data["status"] == "healthy", (
            f"Expected status 'healthy', got '{data['status']}'"
        )
        assert data["model_loaded"] is True, (
            "Model should be loaded in health check"
        )


class TestPredictEndpoint:
    """Tests for the /predict endpoint."""

    def test_predict_endpoint(self, client, sample_application):
        """POST /predict with sample data returns prediction."""
        response = client.post("/predict", json=sample_application)
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}, body: {response.text}"
        )

    def test_predict_response_format(self, client, sample_application):
        """Verify response has correct fields."""
        response = client.post("/predict", json=sample_application)
        data = response.json()

        assert "default_probability" in data, "Response should contain default_probability"
        assert "risk_category" in data, "Response should contain risk_category"
        assert "model_name" in data, "Response should contain model_name"

        # Verify value ranges and types
        assert isinstance(data["default_probability"], float), (
            "default_probability should be float"
        )
        assert 0.0 <= data["default_probability"] <= 1.0, (
            "default_probability should be between 0 and 1"
        )
        assert data["risk_category"] in ["low", "medium", "high"], (
            f"risk_category should be low/medium/high, got '{data['risk_category']}'"
        )
        assert isinstance(data["model_name"], str), "model_name should be string"

    def test_predict_invalid_data(self, client):
        """POST /predict with invalid data returns 422."""
        invalid_data = {
            "checking_account": "A11",
            # Missing most required fields
        }
        response = client.post("/predict", json=invalid_data)
        assert response.status_code == 422, (
            f"Expected 422 for invalid data, got {response.status_code}"
        )


class TestModelInfoEndpoint:
    """Tests for the /model-info endpoint."""

    def test_model_info_endpoint(self, client):
        """GET /model-info returns model info."""
        response = client.get("/model-info")
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        data = response.json()
        assert "model_name" in data, "Response should contain model_name"
        assert "n_features" in data, "Response should contain n_features"
        assert isinstance(data["n_features"], int), "n_features should be int"
        assert data["n_features"] > 0, "n_features should be positive"
