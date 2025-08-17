Quick Start
===========

**Goal:** Build an expert scorecard and use it in ML workflows

**Why this matters:** Expert scorecards combine domain knowledge with ML best practices - they're interpretable, auditable, and production-ready.

Step 1: Install
---------------

.. code-block:: bash

   pip install risk-kit

Step 2: Create a Scorecard
--------------------------

.. code-block:: python

   from risk_kit import ExpertScorecard, NumericFeature, NumericBucket

   scorecard = ExpertScorecard(
       name="Credit Risk",
       features=[
           NumericFeature(
               name="income",
               buckets=[
                   NumericBucket(definition=(0, 50000), score=20),
                   NumericBucket(definition=(50000, float('inf')), score=80)
               ],
               weight=100
           )
       ]
   )

Step 3: Score Customers
-----------------------

.. code-block:: python

   # Score individual customers
   score = scorecard.predict({"income": 75000})
   print(f"Risk Score: {score}")  # Risk Score: 80.0

Step 4: Add More Features
--------------------------

.. code-block:: python

   from risk_kit import ObjectFeature, ObjectBucket

   # Add categorical feature
   scorecard.features.append(
       ObjectFeature(
           name="employment",
           buckets=[
               ObjectBucket(definition="unemployed", score=0),
               ObjectBucket(definition="employed", score=100)
           ],
           weight=30
       )
   )

   # Update weights (must sum to 100)
   scorecard.features[0].weight = 70  # income

   # Score with multiple features
   score = scorecard.predict({"income": 60000, "employment": "employed"})

Step 5: Use in ML Workflows
---------------------------

**Key insight:** ExpertScorecard IS a sklearn estimator - no wrapper needed!

.. code-block:: python

   import pandas as pd
   from sklearn.pipeline import Pipeline
   from sklearn.model_selection import cross_val_score

   # Use directly in sklearn
   scorecard.fit(X_train, y_train)  # No-op for expert scorecards
   predictions = scorecard.predict(X_test)

   # Works in pipelines
   pipeline = Pipeline([('scorecard', scorecard)])

   # Cross-validation works
   scores = cross_val_score(scorecard, X, y, cv=3)

Validation
----------

Validate scorecard integrity:

.. code-block:: python

   from risk_kit.validation import ValidatorRegistry

   # Validate scorecard
   registry = ValidatorRegistry()
   registry.validate(scorecard)

Step 6: Save for Production
---------------------------

.. code-block:: python

   import pickle

   # Pickle for ML workflows (preferred)
   pickle.dump(scorecard, open('model.pkl', 'wb'))
   loaded_model = pickle.load(open('model.pkl', 'rb'))

   # JSON for configuration (human-readable)
   json_data = scorecard.to_json()
   loaded_scorecard = ExpertScorecard.from_json(json_data)

Next Steps
----------

- Check out the :doc:`examples/iris_example` for a complete ML workflow
- Browse the :doc:`api/models` for detailed API documentation
- Learn about :doc:`api/validation` for scorecard quality assurance
