Risk-Kit 🎯
============

**What:** Expert-driven credit risk scorecards with native sklearn compatibility

**Why:** Combines domain expertise with ML best practices - interpretable, auditable, and production-ready

**How:** Define scoring rules, get sklearn estimator

.. code-block:: python

   from risk_kit import ExpertScorecard, NumericFeature, NumericBucket
   from risk_kit.expert_scorecard.validation import ValidatorRegistry, FeatureWeightValidator

   # Create validation registry
   registry = ValidatorRegistry()
   registry.register(FeatureWeightValidator)

   # Define expert scoring rules with validation
   scorecard = ExpertScorecard(
       features=[
           NumericFeature(
               name="income",
               buckets=[
                   NumericBucket(definition=(0, 50000), score=20),
                   NumericBucket(definition=(50000, float('inf')), score=80)
               ],
               weight=100
           )
       ],
       validation_registry=registry
   )

   # Use like any sklearn model
   scorecard.fit(X_train, y_train)
   predictions = scorecard.predict(X_test)

   # Pickle for production
   import pickle
   pickle.dump(scorecard, open('model.pkl', 'wb'))

Installation
------------

.. code-block:: bash

   pip install risk-kit

Core Concepts
=============

**Buckets** → **Features** → **Scorecard** → **Sklearn Model**

Each feature has buckets that assign scores to value ranges. Features are weighted and combined into a scorecard that acts as a standard sklearn estimator.

Getting Started
===============

1. **Install:** ``pip install risk-kit``
2. **Learn:** :doc:`quickstart` (5 minutes)
3. **Example:** :doc:`examples/iris_example` (complete workflow)
4. **Visualize:** :doc:`visualization` (scorecard tables)
5. **Reference:** :doc:`api/index` (full API)

.. toctree::
   :hidden:
   :maxdepth: 1

   quickstart
   examples/iris_example
   visualization
   api/index
