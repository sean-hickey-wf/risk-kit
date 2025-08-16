from pydantic import BaseModel

from risk_kit.expert_scorecard.models.feature import Feature


class Scorecard(BaseModel):
    name: str
    description: str
    version: str
    features: list[Feature]
