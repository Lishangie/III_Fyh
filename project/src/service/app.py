"""FastAPI service for the Credit Risk Scoring API.

Exposes REST endpoints for health checks, credit risk predictions,
and model information.
"""

import logging
from contextlib import asynccontextmanager
from typing import Optional

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.config import load_config
from src.models.predict import CreditScoringModel

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

# Global model reference
_model: Optional[CreditScoringModel] = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler: load model on startup."""
    global _model
    try:
        logger.info("Loading credit risk scoring model...")
        _model = CreditScoringModel()
        logger.info("Model loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        _model = None
    yield
    # Cleanup on shutdown
    _model = None
    logger.info("Model unloaded")


# Create FastAPI app
app = FastAPI(
    title="Credit Risk Scoring API",
    description="API for predicting loan default probability using the German Credit Risk dataset",
    version="1.0.0",
    lifespan=lifespan,
)


# ---- Pydantic Models ----

class CreditApplication(BaseModel):
    """Schema for a credit application with all 20 features."""

    checking_account: str = Field(
        ...,
        description="Status of existing checking account (e.g., A11, A12, A13, A14)",
    )
    duration: int = Field(
        ...,
        description="Duration in months",
        gt=0,
    )
    credit_history: str = Field(
        ...,
        description="Credit history (e.g., A30, A31, A32, A33, A34)",
    )
    purpose: str = Field(
        ...,
        description="Purpose of the loan (e.g., A40, A41, A42, etc.)",
    )
    credit_amount: int = Field(
        ...,
        description="Credit amount",
        gt=0,
    )
    savings_account: str = Field(
        ...,
        description="Savings account/bonds (e.g., A61, A62, A63, A64, A65)",
    )
    employment_since: str = Field(
        ...,
        description="Present employment since (e.g., A71, A72, A73, A74, A75)",
    )
    installment_rate: int = Field(
        ...,
        description="Installment rate in percentage of disposable income",
        gt=0,
    )
    personal_status: str = Field(
        ...,
        description="Personal status and sex (e.g., A91, A92, A93, A94, A95)",
    )
    other_debtors: str = Field(
        ...,
        description="Other debtors/guarantors (e.g., A101, A102, A103)",
    )
    residence_since: int = Field(
        ...,
        description="Present residence since (years)",
        ge=0,
    )
    property_type: str = Field(
        ...,
        alias="property_type",
        description="Property (e.g., A121, A122, A123, A124)",
    )
    age: int = Field(
        ...,
        description="Age in years",
        gt=0,
    )
    other_installment_plans: str = Field(
        ...,
        description="Other installment plans (e.g., A141, A142, A143)",
    )
    housing: str = Field(
        ...,
        description="Housing (e.g., A151, A152, A153)",
    )
    existing_credits: int = Field(
        ...,
        description="Number of existing credits at this bank",
        gt=0,
    )
    job: str = Field(
        ...,
        description="Job (e.g., A171, A172, A173, A174)",
    )
    people_liable: int = Field(
        ...,
        description="Number of people being liable to provide maintenance for",
        ge=1,
    )
    telephone: str = Field(
        ...,
        description="Telephone (e.g., A191, A192)",
    )
    foreign_worker: str = Field(
        ...,
        description="Foreign worker (e.g., A201, A202)",
    )

    model_config = {"populate_by_name": True}


class PredictionResponse(BaseModel):
    """Schema for the prediction response."""

    default_probability: float = Field(
        ...,
        description="Probability of loan default (0.0 to 1.0)",
    )
    risk_category: str = Field(
        ...,
        description="Risk category: low, medium, or high",
    )
    model_name: str = Field(
        ...,
        description="Name of the model used for prediction",
    )


# ---- API Endpoints ----

@app.get("/health")
async def health_check():
    """Health check endpoint.

    Returns the service status and whether the model is loaded.
    """
    model_loaded = _model is not None and _model.health_check()
    status = "healthy" if model_loaded else "degraded"
    return {"status": status, "model_loaded": model_loaded}


@app.post("/predict", response_model=PredictionResponse)
async def predict(application: CreditApplication):
    """Predict the probability of loan default for a credit application.

    Args:
        application: Credit application data with all 20 features.

    Returns:
        PredictionResponse with default_probability, risk_category, and model_name.
    """
    if _model is None or not _model.health_check():
        logger.error("Prediction requested but model is not loaded")
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded. Please try again later.",
        )

    try:
        # Convert Pydantic model to dict, mapping property_type -> property
        features = application.model_dump(by_alias=False)
        # The field is stored as 'property_type' in Python but needs to be
        # 'property' for the preprocessor
        if "property_type" in features:
            features["property"] = features.pop("property_type")

        logger.info(f"Prediction request received for age={features.get('age')}, "
                     f"credit_amount={features.get('credit_amount')}")

        result = _model.predict(features)

        logger.info(f"Prediction result: {result}")

        return PredictionResponse(**result)

    except ValueError as e:
        logger.error(f"Validation error during prediction: {e}")
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        logger.error(f"Unexpected error during prediction: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error during prediction: {str(e)}",
        )


@app.get("/model-info")
async def model_info():
    """Get information about the loaded model.

    Returns the model name and number of features.
    """
    if _model is None or not _model.health_check():
        raise HTTPException(
            status_code=503,
            detail="Model is not loaded.",
        )

    n_features = len(_model.preprocessor.get_feature_names())
    return {
        "model_name": _model.model_name,
        "n_features": n_features,
    }
