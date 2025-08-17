import pytest

from risk_kit.expert_scorecard.models.bucket import (
    NumericBucket,
    NumericDefinitionType,
    ObjectBucket,
    ObjectDefinitionType,
)


def test_numeric_bucket_overlaps_with() -> None:
    bucket_1 = NumericBucket(definition=(1, 2), score=10)
    bucket_2 = NumericBucket(definition=(1.5, 3), score=20)
    assert bucket_1.overlaps_with(bucket_2)
    assert bucket_2.overlaps_with(bucket_1)


def test_numeric_bucket_does_not_overlap_with() -> None:
    # when the values are not the same but are very very close to each other, I think we will run into precision issues
    # and values may be considered the same value but actually not be
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


def test_numeric_bucket_contains() -> None:
    num_bucket = NumericBucket(definition=(1, 2), score=10)
    assert num_bucket.contains(1.5)
    assert not num_bucket.contains(3)
    with pytest.raises(TypeError):
        num_bucket.contains("invalid")

    # Test exact value bucket
    exact_bucket = NumericBucket(definition=5.0, score=20)
    assert exact_bucket.contains(5.0)
    assert not exact_bucket.contains(5.1)


def test_object_bucket_contains() -> None:
    # Test single string bucket
    str_bucket = ObjectBucket(definition="a", score=10)
    assert str_bucket.contains("a")
    assert not str_bucket.contains("b")
    with pytest.raises(TypeError):
        str_bucket.contains(123)

    # Test list bucket
    list_bucket = ObjectBucket(definition=["a", "b", "c"], score=20)
    assert list_bucket.contains("a")
    assert list_bucket.contains("b")
    assert not list_bucket.contains("d")


@pytest.mark.parametrize(
    "definition, expected_sort_key",
    [
        ((1, 2), (0, 10)),
        (1, (1, 10)),
    ],
)
def test_correct_numeric_sort_key_returned(
    definition: NumericDefinitionType, expected_sort_key: tuple[int, float]
) -> None:
    num_bucket = NumericBucket(definition=definition, score=10)
    assert num_bucket.get_sort_key() == expected_sort_key


@pytest.mark.parametrize(
    "definition, expected_sort_key",
    [
        ("a", (1, 10)),
        (["a", "b", "c"], (0, 10)),
    ],
)
def test_correct_object_sort_key_returned(
    definition: ObjectDefinitionType, expected_sort_key: tuple[int, float]
) -> None:
    obj_bucket = ObjectBucket(definition=definition, score=10)
    assert obj_bucket.get_sort_key() == expected_sort_key


def test_numeric_bucket_does_not_overlap_with_close_values() -> None:
    bucket_1 = NumericBucket(definition=(1, 2), score=10)
    bucket_2 = NumericBucket(definition=(2.00000000000000001, 3), score=20)
    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)


def test_overlaps_with_touching_boundaries_both_inclusive() -> None:
    """Test overlaps when boundaries touch and both are inclusive"""
    bucket_1 = NumericBucket(definition=(0, 10), score=100, left_inclusive=True, right_inclusive=True)
    bucket_2 = NumericBucket(definition=(10, 20), score=200, left_inclusive=True, right_inclusive=True)

    # Should overlap because both include 10
    assert bucket_1.overlaps_with(bucket_2)
    assert bucket_2.overlaps_with(bucket_1)


def test_overlaps_with_touching_boundaries_one_inclusive() -> None:
    """Test overlaps when boundaries touch and only one is inclusive"""
    bucket_1 = NumericBucket(definition=(0, 10), score=100, left_inclusive=True, right_inclusive=True)
    bucket_2 = NumericBucket(definition=(10, 20), score=200, left_inclusive=False, right_inclusive=True)

    # Should not overlap because bucket_2 excludes 10
    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)


def test_overlaps_with_touching_boundaries_both_exclusive() -> None:
    """Test overlaps when boundaries touch and both are exclusive"""
    bucket_1 = NumericBucket(definition=(0, 10), score=100, left_inclusive=True, right_inclusive=False)
    bucket_2 = NumericBucket(definition=(10, 20), score=200, left_inclusive=False, right_inclusive=True)

    # Should not overlap because neither includes 10
    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)


def test_overlaps_with_touching_boundaries_complementary_inclusive() -> None:
    """Test overlaps when boundaries touch with complementary inclusivity"""
    bucket_1 = NumericBucket(definition=(0, 10), score=100, left_inclusive=True, right_inclusive=False)
    bucket_2 = NumericBucket(definition=(10, 20), score=200, left_inclusive=True, right_inclusive=False)

    # Should not overlap because bucket_1 excludes 10 and bucket_2 includes it, but no shared value
    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)


def test_display_definition_with_inclusivity_flags() -> None:
    """Test display definition shows correct bracket notation"""
    # [0, 10] - both inclusive
    bucket1 = NumericBucket(definition=(0, 10), score=100, left_inclusive=True, right_inclusive=True)
    assert bucket1.display_definition() == "[0.0, 10.0]"

    # (0, 10) - both exclusive
    bucket2 = NumericBucket(definition=(0, 10), score=100, left_inclusive=False, right_inclusive=False)
    assert bucket2.display_definition() == "(0.0, 10.0)"

    # [0, 10) - left inclusive, right exclusive
    bucket3 = NumericBucket(definition=(0, 10), score=100, left_inclusive=True, right_inclusive=False)
    assert bucket3.display_definition() == "[0.0, 10.0)"

    # (0, 10] - left exclusive, right inclusive
    bucket4 = NumericBucket(definition=(0, 10), score=100, left_inclusive=False, right_inclusive=True)
    assert bucket4.display_definition() == "(0.0, 10.0]"


def test_rounding_error_scenario() -> None:
    """Test the specific rounding error scenario mentioned in the issue"""
    # Bucket 1: [0, 10) - includes 0, excludes 10
    bucket_1 = NumericBucket(definition=(0, 10), score=100, left_inclusive=True, right_inclusive=False)

    # Bucket 2: [10, 20) - includes 10, excludes 20
    bucket_2 = NumericBucket(definition=(10, 20), score=200, left_inclusive=True, right_inclusive=False)

    # Test exact boundary values
    assert not bucket_1.contains(10.0)  # Should not be in bucket_1
    assert bucket_2.contains(10.0)  # Should be in bucket_2

    # Test values that might round to 10
    assert not bucket_1.contains(10.00001)  # Should not be in bucket_1
    assert bucket_2.contains(10.00001)  # Should be in bucket_2

    # Test values just below 10
    assert bucket_1.contains(9.99999)  # Should be in bucket_1
    assert not bucket_2.contains(9.99999)  # Should not be in bucket_2

    # Verify no overlap
    assert not bucket_1.overlaps_with(bucket_2)
    assert not bucket_2.overlaps_with(bucket_1)


def test_contains_with_inclusivity_flags() -> None:
    """Test contains method with different inclusivity combinations"""
    # [0, 10] - both inclusive
    bucket1 = NumericBucket(definition=(0, 10), score=100, left_inclusive=True, right_inclusive=True)
    assert bucket1.contains(0)
    assert bucket1.contains(10)
    assert bucket1.contains(5)
    assert not bucket1.contains(-1)
    assert not bucket1.contains(11)

    # (0, 10) - both exclusive
    bucket2 = NumericBucket(definition=(0, 10), score=100, left_inclusive=False, right_inclusive=False)
    assert not bucket2.contains(0)
    assert not bucket2.contains(10)
    assert bucket2.contains(5)
    assert not bucket2.contains(-1)
    assert not bucket2.contains(11)

    # [0, 10) - left inclusive, right exclusive
    bucket3 = NumericBucket(definition=(0, 10), score=100, left_inclusive=True, right_inclusive=False)
    assert bucket3.contains(0)
    assert not bucket3.contains(10)
    assert bucket3.contains(5)

    # (0, 10] - left exclusive, right inclusive
    bucket4 = NumericBucket(definition=(0, 10), score=100, left_inclusive=False, right_inclusive=True)
    assert not bucket4.contains(0)
    assert bucket4.contains(10)
    assert bucket4.contains(5)
