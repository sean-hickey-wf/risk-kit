import pytest
from logot import Logot, logged

from risk_kit.expert_scorecard.models.bucket import (
    NumericBucket,
    NumericDefinitionType,
    ObjectBucket,
    ObjectDefinitionType,
)


def test_numeric_bucket_overlaps_with() -> None:
    bucket_1 = NumericBucket(definition=(1, 2), score=10)
    bucket_2 = NumericBucket(definition=(1, 3), score=20)
    assert bucket_1.overlaps_with(bucket_2)
    assert bucket_2.overlaps_with(bucket_1)


def test_numeric_bucket_does_not_overlap_with() -> None:
    bucket_1 = NumericBucket(definition=(1, 2), score=10)
    bucket_2 = NumericBucket(definition=(2, 3), score=20)
    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)


def test_object_bucket_overlaps_with() -> None:
    bucket_1 = ObjectBucket(definition="a", score=10)
    bucket_2 = ObjectBucket(definition=["a", "b", "c"], score=20)
    assert bucket_1.overlaps_with(bucket_2)
    assert bucket_2.overlaps_with(bucket_1)


def test_object_bucket_does_not_overlap_with() -> None:
    bucket_1 = ObjectBucket(definition="a", score=10)
    bucket_2 = ObjectBucket(definition="b", score=20)
    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)


def test_overlaps_with_touching_boundaries_both_inclusive() -> None:
    bucket_1 = NumericBucket(definition=(
        0, 10), score=100, left_inclusive=True, right_inclusive=True)
    bucket_2 = NumericBucket(definition=(
        10, 20), score=200, left_inclusive=True, right_inclusive=True)

    assert bucket_1.overlaps_with(bucket_2)
    assert bucket_2.overlaps_with(bucket_1)


def test_overlaps_with_touching_boundaries_one_inclusive() -> None:
    bucket_1 = NumericBucket(definition=(
        0, 10), score=100, left_inclusive=True, right_inclusive=True)
    bucket_2 = NumericBucket(definition=(
        10, 20), score=200, left_inclusive=False, right_inclusive=True)

    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)


def test_overlaps_with_range_and_single_value_bucket() -> None:
    bucket_1 = NumericBucket(definition=10, score=100)
    bucket_2 = NumericBucket(definition=(
        10, 20), score=200, left_inclusive=False, right_inclusive=True)

    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)


def test_overlaps_with_range_and_single_value_bucket_inclusive() -> None:
    bucket_1 = NumericBucket(definition=10, score=100)
    bucket_2 = NumericBucket(definition=(
        10, 20), score=200, left_inclusive=True, right_inclusive=True)

    assert bucket_1.overlaps_with(bucket_2)
    assert bucket_2.overlaps_with(bucket_1)


def test_overlaps_with_touching_boundaries_complementary_inclusive() -> None:
    """Test overlaps when boundaries touch with complementary inclusivity"""
    bucket_1 = NumericBucket(definition=(
        0, 10), score=100, left_inclusive=True, right_inclusive=False)
    bucket_2 = NumericBucket(definition=(
        10, 20), score=200, left_inclusive=True, right_inclusive=False)

    # Should not overlap because bucket_1 excludes 10 and bucket_2 includes it, but no shared value
    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)


def test_display_definition_with_inclusivity_flags() -> None:
    bucket1 = NumericBucket(definition=(0, 10), score=100,
                            left_inclusive=True, right_inclusive=True)
    assert bucket1.display_definition() == "[0.0, 10.0]"

    bucket2 = NumericBucket(definition=(0, 10), score=100,
                            left_inclusive=False, right_inclusive=False)
    assert bucket2.display_definition() == "(0.0, 10.0)"

    bucket3 = NumericBucket(definition=(0, 10), score=100,
                            left_inclusive=True, right_inclusive=False)
    assert bucket3.display_definition() == "[0.0, 10.0)"

    bucket4 = NumericBucket(definition=(0, 10), score=100,
                            left_inclusive=False, right_inclusive=True)
    assert bucket4.display_definition() == "(0.0, 10.0]"


def test_get_score_default_score_returned() -> None:
    num_bucket = NumericBucket(definition=(1, 2), score=10)
    assert num_bucket.get_score(3, 0) == 0

    obj_bucket = ObjectBucket(definition="a", score=10)
    assert obj_bucket.get_score("b", 0) == 0


def test_default_score_warning_logged(logot: Logot) -> None:
    num_bucket = NumericBucket(definition=(1, 2), score=10)
    num_bucket.get_score(3, 0)
    logot.assert_logged(logged.warning("No score found for numeric value: %s"))

    obj_bucket = ObjectBucket(definition="a", score=10)
    obj_bucket.get_score("b", 0)
    logot.assert_logged(logged.warning("No score found for string value: %s"))


@pytest.mark.parametrize("definition, expected_sort_key", [
    ((1, 2), (0, 10)),
    (1, (1, 10)),
])
def test_correct_numeric_sort_key_returned(definition: NumericDefinitionType, expected_sort_key: tuple[int, float]) -> None:
    num_bucket = NumericBucket(definition=definition, score=10)
    assert num_bucket.get_sort_key() == expected_sort_key


@pytest.mark.parametrize("definition, expected_sort_key", [
    ("a", (1, 10)),
    (["a", "b", "c"], (0, 10)),
])
def test_correct_object_sort_key_returned(definition: ObjectDefinitionType, expected_sort_key: tuple[int, float]) -> None:
    obj_bucket = ObjectBucket(definition=definition, score=10)
    assert obj_bucket.get_sort_key() == expected_sort_key


# Tests for boundary conditions with inclusivity flags
def test_get_score_with_left_inclusive_right_exclusive() -> None:
    """Test default behavior: left inclusive, right exclusive [0, 10)"""
    bucket = NumericBucket(definition=(0, 10), score=100,
                           left_inclusive=True, right_inclusive=False)

    # Should include left boundary
    assert bucket.get_score(0, -1) == 100
    assert bucket.get_score(0.0, -1) == 100

    # Should exclude right boundary
    assert bucket.get_score(10, -1) == -1
    assert bucket.get_score(10.0, -1) == -1

    # Should include values in between
    assert bucket.get_score(5, -1) == 100
    assert bucket.get_score(9.999, -1) == 100

    # Should exclude values outside
    assert bucket.get_score(-0.001, -1) == -1
    assert bucket.get_score(10.001, -1) == -1


def test_get_score_with_left_exclusive_right_inclusive() -> None:
    """Test (0, 10] - left exclusive, right inclusive"""
    bucket = NumericBucket(definition=(0, 10), score=100,
                           left_inclusive=False, right_inclusive=True)

    # Should exclude left boundary
    assert bucket.get_score(0, -1) == -1
    assert bucket.get_score(0.0, -1) == -1

    # Should include right boundary
    assert bucket.get_score(10, -1) == 100
    assert bucket.get_score(10.0, -1) == 100

    # Should include values in between
    assert bucket.get_score(5, -1) == 100
    assert bucket.get_score(0.001, -1) == 100

    # Should exclude values outside
    assert bucket.get_score(-0.001, -1) == -1
    assert bucket.get_score(10.001, -1) == -1


def test_get_score_with_both_inclusive() -> None:
    """Test [0, 10] - both inclusive"""
    bucket = NumericBucket(definition=(0, 10), score=100,
                           left_inclusive=True, right_inclusive=True)

    # Should include both boundaries
    assert bucket.get_score(0, -1) == 100
    assert bucket.get_score(10, -1) == 100

    # Should include values in between
    assert bucket.get_score(5, -1) == 100

    # Should exclude values outside
    assert bucket.get_score(-0.001, -1) == -1
    assert bucket.get_score(10.001, -1) == -1


def test_get_score_with_both_exclusive() -> None:
    """Test (0, 10) - both exclusive"""
    bucket = NumericBucket(definition=(0, 10), score=100,
                           left_inclusive=False, right_inclusive=False)

    # Should exclude both boundaries
    assert bucket.get_score(0, -1) == -1
    assert bucket.get_score(10, -1) == -1

    # Should include values in between
    assert bucket.get_score(5, -1) == 100
    assert bucket.get_score(0.001, -1) == 100
    assert bucket.get_score(9.999, -1) == 100

    # Should exclude values outside
    assert bucket.get_score(-0.001, -1) == -1
    assert bucket.get_score(10.001, -1) == -1


def test_rounding_error_scenario() -> None:
    """Test the specific rounding error scenario mentioned in the issue"""
    bucket_1 = NumericBucket(definition=(
        0, 10), score=100, left_inclusive=True, right_inclusive=False)
    bucket_2 = NumericBucket(definition=(
        10, 20), score=200, left_inclusive=True, right_inclusive=False)

    # Test exact boundary values
    assert bucket_1.get_score(10.0, -1) == -1  # Should not be in bucket_1
    assert bucket_2.get_score(10.0, -1) == 200  # Should be in bucket_2

    # Test values that might round to 10
    assert bucket_1.get_score(10.00001, -1) == -1  # Should not be in bucket_1
    assert bucket_2.get_score(10.00001, -1) == 200  # Should be in bucket_2

    # Test values just below 10
    assert bucket_1.get_score(9.99999, -1) == 100  # Should be in bucket_1
    assert bucket_2.get_score(9.99999, -1) == -1  # Should not be in bucket_2

    # Verify no overlap
    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)
