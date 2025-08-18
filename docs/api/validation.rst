Validation
==========

Validation framework for ensuring scorecard integrity and business rule compliance.

Overview
--------

The validation system allows you to define and enforce business rules when creating scorecards. You create a ``ValidatorRegistry``, register validators with it, and then pass it to the ``ExpertScorecard`` constructor to automatically validate your scorecard.

Quick Example
-------------

.. code-block:: python

   from risk_kit.expert_scorecard.models import ExpertScorecard, NumericFeature, NumericBucket
   from risk_kit.expert_scorecard.validation import ValidatorRegistry, FeatureWeightValidator, OverlapValidator

   # Create a validation registry
   registry = ValidatorRegistry()

   # Register built-in validators
   registry.register(FeatureWeightValidator)
   registry.register(OverlapValidator)

   # Create scorecard with validation
   scorecard = ExpertScorecard(
       features=[
           NumericFeature(
               name="age",
               buckets=[
                   NumericBucket(definition=(18.0, 30.0), score=100.0),
                   NumericBucket(definition=(30.0, 50.0), score=50.0),
                   NumericBucket(definition=(50.0, 80.0), score=25.0),
               ],
               weight=60.0
           )
       ],
       validation_registry=registry  # Validation runs automatically during construction
   )

   # Check validation results
   print("Validation passed!" if scorecard.validation_results else "No validation configured")
   for result in scorecard.validation_results:
       print(f"Validator: {result.validator_name} - Validated at: {result.validated_at}")

Custom Validation Example
--------------------------

You can create custom validators by extending the ``ScorecardValidator`` base class:

.. code-block:: python

   from risk_kit.expert_scorecard.validation import ScorecardValidator
   from risk_kit.expert_scorecard.models import ExpertScorecard

   class MinimumFeaturesValidator(ScorecardValidator):
       """Ensures scorecard has at least a minimum number of features."""

       name = "minimum_features_validator"

       def __init__(self, min_features: int = 2):
           self.min_features = min_features

       def validate(self, scorecard: ExpertScorecard) -> None:
           if len(scorecard.features) < self.min_features:
               raise ValueError(
                   f"Scorecard must have at least {self.min_features} features, "
                   f"but has {len(scorecard.features)}"
               )

   class MaximumScoreValidator(ScorecardValidator):
       """Ensures no individual bucket score exceeds a maximum value."""

       name = "maximum_score_validator"

       def __init__(self, max_score: float = 100.0):
           self.max_score = max_score

       def validate(self, scorecard: ExpertScorecard) -> None:
           for feature in scorecard.features:
               for bucket in feature.buckets:
                   if bucket.score > self.max_score:
                       raise ValueError(
                           f"Bucket score {bucket.score} in feature '{feature.name}' "
                           f"exceeds maximum allowed score of {self.max_score}"
                       )

   # Create registry with custom validators
   custom_registry = ValidatorRegistry()
   custom_registry.register(MinimumFeaturesValidator)
   custom_registry.register(MaximumScoreValidator)
   custom_registry.register(FeatureWeightValidator)

   # Create scorecard with custom validation
   try:
       scorecard = ExpertScorecard(
           features=[
               NumericFeature(
                   name="income",
                   buckets=[
                       NumericBucket(definition=(0.0, 50000.0), score=20.0),
                       NumericBucket(definition=(50000.0, 100000.0), score=80.0),
                   ],
                   weight=100.0
               )
           ],
           validation_registry=custom_registry
       )
       print("Scorecard created successfully with custom validation!")
   except ValueError as e:
       print(f"Validation failed: {e}")

Registry Management
-------------------

.. code-block:: python

   # Create empty registry
   registry = ValidatorRegistry()

   # Register multiple validators
   registry.register(FeatureWeightValidator)
   registry.register(OverlapValidator)

   # Check registered validators
   print("Registered validators:", list(registry.validators.keys()))

   # Clear all validators
   registry.clear()
   print("After clearing:", list(registry.validators.keys()))

API Reference
=============

Registry
--------

.. autoclass:: risk_kit.expert_scorecard.validation.ValidatorRegistry
   :members:

Base Classes
------------

.. autoclass:: risk_kit.expert_scorecard.validation.ScorecardValidator
   :members:

Built-in Validators
-------------------

.. autoclass:: risk_kit.expert_scorecard.validation.FeatureWeightValidator
   :members:

.. autoclass:: risk_kit.expert_scorecard.validation.OverlapValidator
   :members:
