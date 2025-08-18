from __future__ import annotations

from datetime import datetime
from typing import Any

import numpy as np
import pandas as pd
from pydantic import BaseModel
from sklearn.base import BaseEstimator, RegressorMixin

from risk_kit.expert_scorecard.models.feature import FeatureTableRow, NumericFeature, ObjectFeature
from risk_kit.expert_scorecard.validation.registry import ValidatorRegistry

AnyFeature = NumericFeature | ObjectFeature


class ValidationResult(BaseModel):
    """Metadata about validation that was performed - Good for debugging and auditing"""

    validator_name: str
    validated_at: datetime
    passed: bool
    error_message: str | None = None


class ExpertScorecard(BaseEstimator, RegressorMixin):

    def __init__(
        self,
        features: list[AnyFeature],
        validation_registry: ValidatorRegistry | None = None,
    ) -> None:
        self.features = features
        self.validation_registry = validation_registry
        self.validation_results: list[ValidationResult] = []
        self.validate()
        self.is_fitted_ = True

    def validate(self) -> ExpertScorecard:
        if self.validation_registry is not None:
            for validator in self.validation_registry.validators.values():
                validator.validate(self)
                self.validation_results.append(
                    ValidationResult(validator_name=validator.name, validated_at=datetime.now(), passed=True)
                )
        return self

    @property
    def feature_names_(self) -> list[str]:
        """Sklearn-compatible feature names property."""
        return [feature.name for feature in self.features]

    def get_params(self, deep: bool = True) -> dict[str, Any]:
        """Get parameters for this estimator."""
        return {
            "model": self.__class__.__name__,
            "features": [feature.model_dump() for feature in self.features],
            "validation_results": [result.model_dump() for result in self.validation_results],
        }

    def fit(self, X: Any, y: Any = None, **fit_params: Any) -> ExpertScorecard:
        """Fit is a no-op for expert scorecards - they are pre-trained."""
        return self

    def predict(self, X: Any) -> np.ndarray:
        """Calculate risk scores for input data (sklearn-compatible)."""
        # Convert input to consistent format
        if isinstance(X, pd.DataFrame):
            return np.array([self._score_record(row.to_dict()) for _, row in X.iterrows()])
        elif isinstance(X, dict):
            return np.array([self._score_record(X)])
        elif isinstance(X, np.ndarray):
            if X.ndim == 1:
                record = dict(zip(self.feature_names_, X, strict=True))
                return np.array([self._score_record(record)])
            else:
                return np.array([self._score_record(dict(zip(self.feature_names_, row, strict=True))) for row in X])
        else:
            raise ValueError(f"X must be pandas DataFrame, dict, or numpy array, got {type(X).__name__}")

    def _score_record(self, record: dict[str, Any]) -> float:
        """Score a single record (dictionary of feature values)."""
        total_score = 0.0
        for feature in self.features:
            if feature.name in record:
                feature_score = feature.get_score(record[feature.name])
                total_score += (feature_score * feature.weight) / 100.0
        return total_score

    def predict_single(self, X: dict[str, Any]) -> float:
        """Score a single record (original interface for backward compatibility)."""
        return self._score_record(X)

    def score(self, X: Any, y: Any) -> np.ndarray:
        """Return the predicted scores (sklearn-compatible)."""
        return self.predict(X)

    def get_table_data(self) -> tuple[list[str], list[FeatureTableRow]]:
        headers = list(FeatureTableRow.model_fields.keys())
        rows = [row for feature in self.features for row in feature.get_feature_rows()]
        return headers, rows

    def get_score_range(self) -> tuple[float, float]:
        min_score = min(feature.get_score_range()[0] for feature in self.features)
        max_score = max(feature.get_score_range()[1] for feature in self.features)
        return (min_score, max_score)
