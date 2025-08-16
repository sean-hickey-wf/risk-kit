"""
Risk-Kit: An open-source expert scorecard framework for credit risk modeling.

Risk-Kit provides a comprehensive set of tools for creating, managing, and deploying
expert-driven credit risk scorecards. Built on Pydantic for robust data validation
and serialization, it enables transparent, auditable, and version-controlled
risk modeling workflows.

Key Features:
- Expert-driven scorecard creation with transparent business logic
- Robust data validation and type safety through Pydantic models
- Version control and auditability for regulatory compliance
- JSON serialization for easy integration with production systems
- Interactive UI for non-technical users (optional dependency)

Example:
    >>> from risk_kit.scorecard import Scorecard, Feature, Bucket
    >>> # Create a simple scorecard
    >>> age_feature = Feature(
    ...     name="age",
    ...     description="Applicant age in years",
    ...     buckets=[
    ...         Bucket(definition=(18, 25), points=10),
    ...         Bucket(definition=(26, 65), points=20),
    ...         Bucket(definition=(66, 100), points=5),
    ...     ],
    ...     weight=30.0
    ... )
"""

# Import main classes for convenient access
# from risk_kit.expert_scorecard.engine import calculate_score
from risk_kit.expert_scorecard.models import Bucket, Feature, Scorecard

__all__ = [
    "Bucket",
    "Feature",
    "Scorecard",
    # "calculate_score",
    "__version__",
]
