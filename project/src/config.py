"""Configuration module for the Credit Risk Scoring service.

Loads settings from configs/config.yaml and environment variables.
"""

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

import yaml


# Project root is the directory containing this project
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Standard directories
DATA_DIR = PROJECT_ROOT / "data"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
CONFIGS_DIR = PROJECT_ROOT / "configs"


@dataclass
class ModelConfig:
    """Configuration for model training and evaluation."""

    name: str = "credit_risk_scoring"
    version: str = "1.0.0"
    random_state: int = 42
    test_size: float = 0.15
    val_size: float = 0.15


@dataclass
class ServiceConfig:
    """Configuration for the FastAPI service."""

    host: str = "0.0.0.0"
    port: int = 8000


@dataclass
class RiskThresholds:
    """Risk category thresholds for default probability."""

    low: float = 0.3
    high: float = 0.6


@dataclass
class AppConfig:
    """Top-level application configuration."""

    model: ModelConfig = field(default_factory=ModelConfig)
    service: ServiceConfig = field(default_factory=ServiceConfig)
    risk_thresholds: RiskThresholds = field(default_factory=RiskThresholds)


def load_config(config_path: Optional[str] = None) -> AppConfig:
    """Load configuration from YAML file and environment variables.

    Args:
        config_path: Optional path to config file. Defaults to
            configs/config.yaml under the project root.

    Returns:
        AppConfig instance with loaded settings.
    """
    if config_path is None:
        config_path = str(CONFIGS_DIR / "config.yaml")

    config_data: Dict[str, Any] = {}

    # Load YAML config if it exists
    if os.path.exists(config_path):
        with open(config_path, "r") as f:
            config_data = yaml.safe_load(f) or {}

    # Build ModelConfig, allowing env var overrides
    model_section = config_data.get("model", {})
    model_config = ModelConfig(
        name=os.environ.get("MODEL_NAME", model_section.get("name", "credit_risk_scoring")),
        version=os.environ.get("MODEL_VERSION", model_section.get("version", "1.0.0")),
        random_state=int(os.environ.get("RANDOM_STATE", model_section.get("random_state", 42))),
        test_size=float(os.environ.get("TEST_SIZE", model_section.get("test_size", 0.15))),
        val_size=float(os.environ.get("VAL_SIZE", model_section.get("val_size", 0.15))),
    )

    # Build ServiceConfig, allowing env var overrides
    service_section = config_data.get("service", {})
    service_config = ServiceConfig(
        host=os.environ.get("SERVICE_HOST", service_section.get("host", "0.0.0.0")),
        port=int(os.environ.get("SERVICE_PORT", service_section.get("port", 8000))),
    )

    # Build RiskThresholds, allowing env var overrides
    risk_section = config_data.get("risk_thresholds", {})
    risk_thresholds = RiskThresholds(
        low=float(os.environ.get("RISK_THRESHOLD_LOW", risk_section.get("low", 0.3))),
        high=float(os.environ.get("RISK_THRESHOLD_HIGH", risk_section.get("high", 0.6))),
    )

    return AppConfig(
        model=model_config,
        service=service_config,
        risk_thresholds=risk_thresholds,
    )
