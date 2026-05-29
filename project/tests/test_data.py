"""Unit tests for data loading and preprocessing."""

import pytest
import pandas as pd
import numpy as np

from src.data.loader import load_german_credit
from src.data.preprocessing import (
    CreditPreprocessor,
    CATEGORICAL_FEATURES,
    NUMERICAL_FEATURES,
)


class TestLoadGermanCredit:
    """Tests for the load_german_credit function."""

    @pytest.fixture(scope="class")
    def df(self):
        """Load the dataset once for all tests in this class."""
        return load_german_credit()

    def test_load_german_credit_shape(self, df):
        """Verify dataset has 1000 rows and 21 columns (20 features + target)."""
        assert df.shape[0] == 1000, f"Expected 1000 rows, got {df.shape[0]}"
        assert df.shape[1] == 21, f"Expected 21 columns, got {df.shape[1]}"

    def test_load_german_credit_target(self, df):
        """Verify target values are 0 and 1."""
        unique_values = sorted(df["class"].unique())
        assert unique_values == [0, 1], (
            f"Expected target values [0, 1], got {unique_values}"
        )

    def test_no_missing_values(self, df):
        """Verify no NaN in dataset."""
        missing_count = df.isnull().sum().sum()
        assert missing_count == 0, f"Expected 0 missing values, got {missing_count}"

    def test_numerical_features(self, df):
        """Verify all numerical features exist in dataset."""
        for feature in NUMERICAL_FEATURES:
            assert feature in df.columns, (
                f"Numerical feature '{feature}' not found in dataset columns"
            )

    def test_categorical_features(self, df):
        """Verify all categorical features exist in dataset."""
        for feature in CATEGORICAL_FEATURES:
            assert feature in df.columns, (
                f"Categorical feature '{feature}' not found in dataset columns"
            )


class TestCreditPreprocessor:
    """Tests for the CreditPreprocessor class."""

    @pytest.fixture(scope="class")
    def df(self):
        """Load the dataset once for all tests in this class."""
        return load_german_credit()

    @pytest.fixture(scope="class")
    def preprocessor(self, df):
        """Fit a preprocessor on the dataset."""
        X = df.drop(columns=["class"])
        prep = CreditPreprocessor()
        prep.fit(X)
        return prep

    def test_preprocessor_fit_transform(self, df):
        """Verify preprocessor output shape."""
        X = df.drop(columns=["class"])
        prep = CreditPreprocessor()
        X_processed = prep.fit_transform(X)

        n_features = len(CATEGORICAL_FEATURES) + len(NUMERICAL_FEATURES)
        assert X_processed.shape[0] == 1000, (
            f"Expected 1000 rows, got {X_processed.shape[0]}"
        )
        assert X_processed.shape[1] == n_features, (
            f"Expected {n_features} columns, got {X_processed.shape[1]}"
        )

    def test_preprocessor_save_load(self, df, tmp_path):
        """Verify preprocessor can be saved and loaded."""
        X = df.drop(columns=["class"])
        prep = CreditPreprocessor()
        prep.fit(X)

        # Save
        save_path = str(tmp_path / "preprocessor.pkl")
        prep.save(save_path)

        # Load
        loaded_prep = CreditPreprocessor.load(save_path)

        # Verify loaded preprocessor produces same results
        X_transformed_original = prep.transform(X)
        X_transformed_loaded = loaded_prep.transform(X)

        np.testing.assert_array_almost_equal(
            X_transformed_original,
            X_transformed_loaded,
            decimal=6,
            err_msg="Loaded preprocessor produces different results",
        )

    def test_preprocessor_feature_names(self, preprocessor):
        """Verify preprocessor returns correct feature names."""
        feature_names = preprocessor.get_feature_names()
        expected_count = len(CATEGORICAL_FEATURES) + len(NUMERICAL_FEATURES)
        assert len(feature_names) == expected_count, (
            f"Expected {expected_count} feature names, got {len(feature_names)}"
        )

    def test_preprocessor_is_fitted(self, preprocessor):
        """Verify preprocessor is fitted after fit()."""
        assert preprocessor._is_fitted is True, "Preprocessor should be fitted"

    def test_preprocessor_transform_before_fit_raises(self, df):
        """Verify transform raises error if called before fit."""
        X = df.drop(columns=["class"])
        prep = CreditPreprocessor()
        with pytest.raises(RuntimeError, match="must be fitted"):
            prep.transform(X)
