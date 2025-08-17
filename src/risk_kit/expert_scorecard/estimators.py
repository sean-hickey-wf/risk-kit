from __future__ import annotations

import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, RegressorMixin
from sklearn.utils.validation import check_is_fitted

from risk_kit.expert_scorecard.models import ExpertScorecard


def to_sklearn(scorecard: ExpertScorecard) -> ScorecardEstimator:
    """Convert ExpertScorecard to sklearn-compatible estimator."""
    return ScorecardEstimator(scorecard=scorecard)


class ScorecardEstimator(BaseEstimator, RegressorMixin):
    """
    Scikit-learn compatible wrapper for ExpertScorecard.

    This estimator allows expert scorecards to be used in sklearn pipelines,
    grid searches, and other sklearn workflows.

    Parameters
    ----------
    scorecard : ExpertScorecard
        The expert scorecard to wrap
    """

    def __init__(self, scorecard: ExpertScorecard):
        self.scorecard = scorecard
        self.feature_names_ = self.scorecard.feature_names

    def fit(self, X, y=None, **fit_params) -> ScorecardEstimator:  # type: ignore
        """Fit is a no-op for expert scorecards so we just return the estimator and set the fitted state to True"""
        self.is_fitted_ = True
        return self

    def predict(self, X) -> np.ndarray:  # type: ignore
        """Calculate risk scores for input data."""
        check_is_fitted(self)

        # Convert input to consistent format
        if isinstance(X, pd.DataFrame):
            return np.array([self._score_record(row.to_dict()) for _, row in X.iterrows()])
        elif isinstance(X, dict):
            return np.array([self._score_record(X)])
        elif isinstance(X, np.ndarray):
            if not hasattr(self, "feature_names_"):
                raise ValueError("Cannot predict with numpy array: no feature names available")
            if X.ndim == 1:
                record = dict(zip(self.feature_names_, X, strict=True))
                return np.array([self._score_record(record)])
            else:
                return np.array([self._score_record(dict(zip(self.feature_names_, row, strict=True))) for row in X])
        else:
            raise ValueError("X must be pandas DataFrame, dict, or numpy array, " f"got {type(X).__name__}")

    def _score_record(self, record: dict) -> float:  # type: ignore
        """Score a single record (dictionary of feature values)."""
        return self.scorecard.predict(record)

    def score(self, X, y) -> np.ndarray:  # type: ignore
        """
        Return the predicted scores for the input data. This is a no-op for expert scorecards so we just return the predicted scores.
        """
        y_pred = self.predict(X)
        return y_pred

    def get_params(self, deep=True) -> dict:  # type: ignore
        """Get parameters for this estimator."""
        params = super().get_params(deep=deep)
        if deep and hasattr(self.scorecard, "get_params"):
            # Include scorecard parameters if available
            scorecard_params = {f"scorecard__{k}": v for k, v in self.scorecard.get_params().items()}
            params.update(scorecard_params)
        return params
