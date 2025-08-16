import logging
from abc import ABC, abstractmethod
from typing import Any

from pydantic import BaseModel

logger = logging.getLogger(__name__)

NumericDefinitionType = tuple[float, float] | float
ObjectDefinitionType = str | list[str]
BucketDefinitionType = NumericDefinitionType | ObjectDefinitionType


class Bucket(BaseModel, ABC):
    """
    Abstract base class for all bucket types.
    Subclasses must implement get_points and get_sort_key methods.
    """
    definition: BucketDefinitionType
    points: float

    @abstractmethod
    def get_points(self, value:  float | str, default: float) -> float:
        """Get points for a given value, return default if no match"""
        pass

    @abstractmethod
    def get_sort_key(self) -> tuple[int, Any]:
        """Generate a sort key for natural ordering of buckets"""
        pass

    @abstractmethod
    def overlaps_with(self, other: 'Bucket') -> bool:
        """Check if this bucket overlaps with another bucket of the same type"""
        pass


class NumericBucket(Bucket):
    """
    Bucket for numeric values. Supports exact values (int/float) or ranges (tuple).
    """
    definition: NumericDefinitionType

    def get_points(self, value: float | str, default: float) -> float:
        if not isinstance(value, float):
            raise TypeError(
                f"NumericBucket only accepts float values, got {type(value).__name__}: {value}")

        if isinstance(self.definition, tuple):
            if self.definition[0] <= value <= self.definition[1]:
                return self.points
        elif isinstance(self.definition, float):
            if value == self.definition:
                return self.points

        logger.debug(
            f"No points found for numeric value: {value} in bucket: {self.definition}")
        return default

    def get_sort_key(self) -> tuple[int, float]:
        """Sort ranges first by lower bound, then exact values"""
        if isinstance(self.definition, tuple):
            return (0, self.definition[0])
        else:
            return (1, self.definition)

    def overlaps_with(self, other: 'Bucket') -> bool:
        """Check if this numeric bucket overlaps with another numeric bucket"""
        if not isinstance(other, NumericBucket):
            return False

        # Get ranges for both buckets
        self_range = self._get_range()
        other_range = other._get_range()

        # Check for overlap: ranges overlap if max(start1, start2) <= min(end1, end2)
        return max(self_range[0], other_range[0]) <= min(self_range[1], other_range[1])

    def _get_range(self) -> tuple[float, float]:
        """Get the range covered by this bucket"""
        if isinstance(self.definition, tuple):
            return self.definition
        else:
            # Exact value is treated as a range [value, value]
            return (float(self.definition), float(self.definition))


class ObjectBucket(Bucket):
    """
    Bucket for string/categorical values. Supports single strings or lists of strings.
    """
    definition: ObjectDefinitionType

    def get_points(self, value: float | str, default: float) -> float:
        if not isinstance(value, str):
            raise TypeError(
                f"ObjectBucket only accepts string values, got {type(value).__name__}: {value}")

        if isinstance(self.definition, str):
            if value == self.definition:
                return self.points
        elif isinstance(self.definition, list):
            if value in self.definition:
                return self.points

        logger.debug(
            f"No points found for string value: {value} in bucket: {self.definition}")
        return default

    def get_sort_key(self) -> tuple[int, str]:
        """Sort single strings before lists, alphabetically within each type"""
        if isinstance(self.definition, str):
            return (2, self.definition)
        else:
            return (3, str(self.definition[0]) if self.definition else "")

    def overlaps_with(self, other: 'Bucket') -> bool:
        """Check if this object bucket overlaps with another object bucket"""
        if not isinstance(other, ObjectBucket):
            return False

        # Get sets of values for both buckets
        self_values = self._get_values()
        other_values = other._get_values()

        # Check for intersection
        return bool(self_values.intersection(other_values))

    def _get_values(self) -> set[str]:
        """Get the set of values covered by this bucket"""
        if isinstance(self.definition, str):
            return {self.definition}
        else:
            return set(self.definition)
