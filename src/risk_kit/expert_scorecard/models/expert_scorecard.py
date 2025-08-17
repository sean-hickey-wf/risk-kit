from __future__ import annotations

from typing import Any

from pydantic import BaseModel

from risk_kit.expert_scorecard.models.feature import NumericFeature, ObjectFeature

AnyFeature = NumericFeature | ObjectFeature


class ExpertScorecard(BaseModel):
    name: str
    description: str
    version: str
    features: list[AnyFeature]

    @property
    def feature_names(self) -> list[str]:
        return [feature.name for feature in self.features]

    def get_params(self) -> dict[str, Any]:
        return self.model_dump()

    def predict(self, X: dict[str, Any]) -> float:
        total_score = 0.0
        for feature in self.features:
            if feature.name in X:
                feature_score = feature.get_score(X[feature.name])
                total_score += (feature_score * feature.weight) / 100.0
        return total_score

    @classmethod
    def from_json(cls, json_str: str) -> ExpertScorecard:
        return cls.model_validate_json(json_str)

    def to_json(self) -> str:
        return self.model_dump_json()

    def get_table_data(self) -> dict[str, list[dict[str, str]]]:
        return {feature.name: feature.get_table_rows() for feature in self.features}
