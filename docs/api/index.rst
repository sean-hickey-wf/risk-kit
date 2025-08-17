API Reference
=============

Complete API documentation for Risk-Kit components.

Core Models
-----------

.. toctree::
   :maxdepth: 2

   models

Validation System
-----------------

.. toctree::
   :maxdepth: 2

   validation

Scikit-learn Integration
------------------------

.. toctree::
   :maxdepth: 2

   estimators

Quick Reference
---------------

**Core Classes:**

* :class:`~risk_kit.expert_scorecard.models.ExpertScorecard` - Main scorecard container (sklearn-compatible)
* :class:`~risk_kit.expert_scorecard.models.NumericFeature` - Numeric features with ranges
* :class:`~risk_kit.expert_scorecard.models.ObjectFeature` - Categorical features
* :class:`~risk_kit.expert_scorecard.models.NumericBucket` - Numeric value buckets
* :class:`~risk_kit.expert_scorecard.models.ObjectBucket` - Categorical value buckets

**Validation:**

* :class:`~risk_kit.expert_scorecard.validation.ValidatorRegistry` - Validation management
* :class:`~risk_kit.expert_scorecard.validation.FeatureWeightValidator` - Weight validation
* :class:`~risk_kit.expert_scorecard.validation.OverlapValidator` - Bucket overlap detection

**Scikit-learn:**

* :class:`~risk_kit.expert_scorecard.estimators.ScorecardEstimator` - Sklearn-compatible estimator
* :func:`~risk_kit.expert_scorecard.estimators.to_sklearn` - Conversion utility
