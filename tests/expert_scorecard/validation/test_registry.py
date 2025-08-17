from collections.abc import Generator

import pytest

from risk_kit.expert_scorecard.models import ExpertScorecard, NumericBucket, NumericFeature
from risk_kit.expert_scorecard.validation.registry import ValidatorRegistry
from risk_kit.expert_scorecard.validation.validators import FeatureWeightValidator, OverlapValidator


@pytest.fixture
def registry() -> Generator[ValidatorRegistry, None, None]:
    registry = ValidatorRegistry()
    yield registry
    registry.clear()


@pytest.fixture
def scorecard_with_invalid_feature_weight() -> ExpertScorecard:
    return ExpertScorecard(
        name="Test Scorecard",
        description="Test Scorecard",
        version="1.0.0",
        features=[
            NumericFeature(
                name="Feature 1",
                family="Test",
                description="Test",
                buckets=[NumericBucket(definition=(0, 100), score=100)],
                weight=150,
            )
        ],
    )


def test_duplicated_validator_name_errors(registry: ValidatorRegistry) -> None:
    registry.register(FeatureWeightValidator)
    with pytest.raises(ValueError):
        registry.register(FeatureWeightValidator)


def test_list_of_validators(registry: ValidatorRegistry) -> None:
    registry.register(FeatureWeightValidator)
    registry.register(OverlapValidator)

    expected_validators = {"feature_weight": FeatureWeightValidator, "overlap": OverlapValidator}
    assert registry.validators == expected_validators
