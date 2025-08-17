"""
Expert scorecard module for Risk-Kit.

This module provides the core functionality for creating, validating, and
executing expert-driven credit risk scorecards. It includes:

- Pydantic data models for scorecard components (Bucket, Feature, Scorecard)
- Score calculation engine with robust validation
- JSON serialization for system integration
- Custom validators for business rule enforcement

Classes:
    Bucket: Abstract base class for all bucket types
    NumericBucket: Bucket for numeric values (ranges or exact values)
    ObjectBucket: Bucket for categorical/string values
    Feature: Represents a characteristic with buckets and weight
    Scorecard: Top-level container for features and metadata

Functions:
    calculate_score: Calculate risk score for given input data
"""

from .models import (
    BaseFeature,
    Bucket,
    ExpertScorecard,
    NumericBucket,
    NumericFeature,
    ObjectBucket,
    ObjectFeature,
)

__all__ = [
    "Bucket",
    "NumericBucket",
    "ObjectBucket",
    "BaseFeature",
    "NumericFeature",
    "ObjectFeature",
    "ExpertScorecard",
]
