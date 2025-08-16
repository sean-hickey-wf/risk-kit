import logging

from pydantic import BaseModel, Field, model_validator

from risk_kit.expert_scorecard.models.bucket import Bucket

logger = logging.getLogger(__name__)


class Feature(BaseModel):
    name: str
    family: str | None = Field(
        default=None, description="The family of the feature. Useful for grouping features together and understanding the dominance of feature families.")
    description: str
    buckets: list[Bucket]
    weight: float
    default_points: float = 0.0

    def get_score(self, value: int | float | str) -> float:
        for bucket in self.buckets:
            points = bucket.get_points(value, self.default_points)
            if points != self.default_points:
                return points
        return self.default_points

    @model_validator(mode="after")
    def order_buckets(self) -> "Feature":
        # Sort buckets for visual purposes - doesn't change functionality
        self.buckets.sort(key=lambda x: x.get_sort_key())
        return self

    def has_overlapping_buckets(self) -> bool:
        """Check if any buckets in this feature overlap with each other"""
        for i, bucket1 in enumerate(self.buckets):
            for bucket2 in self.buckets[i+1:]:
                if bucket1.overlaps_with(bucket2):
                    return True
        return False

    def get_overlapping_buckets(self) -> list[tuple[Bucket, Bucket]]:
        """Get all pairs of overlapping buckets in this feature"""
        overlaps = []
        for i, bucket1 in enumerate(self.buckets):
            for bucket2 in self.buckets[i+1:]:
                if bucket1.overlaps_with(bucket2):
                    overlaps.append((bucket1, bucket2))
        return overlaps
