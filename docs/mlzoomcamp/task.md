# Midterm Project 

The idea is that you now apply everything we learned so far yourself:

### [Module 1: Introduction to Machine Learning](01-intro/)

Learn what machine learning is, when to use it, and how to structure a machine learning project with the CRISP-DM framework.

In this module, you will:

- Compare machine learning systems with rule-based systems.
- Learn the foundations of supervised learning.
- Use CRISP-DM to organize a machine learning project.
- Understand the basic model-selection process.
- Set up the course development environment.

Outcome: a structured approach to framing machine learning problems and starting a reproducible project.

### [Module 2: Machine Learning for Regression](02-regression/)

Build a car-price prediction model while learning the foundations of regression.

In this module, you will:

- Explore and prepare a real dataset.
- Implement linear regression from scratch and with scikit-learn.
- Create and select useful features.
- Apply regularization.
- Validate and compare regression models.

Outcome: a regression model built through a repeatable process from exploratory analysis to validation.

### [Module 3: Machine Learning for Classification](03-classification/)

Build a customer-churn prediction system with logistic regression.

In this module, you will:

- Train and use logistic regression models.
- Encode categorical variables.
- Measure and interpret feature importance.
- Select useful features.
- Interpret a model's predictions.

Outcome: a classification model that estimates customer-churn risk from structured data.

### [Module 4: Evaluation Metrics for Classification](04-evaluation/)

Learn how to evaluate classification systems and choose metrics that match the problem.

In this module, you will:

- Work with accuracy, precision, recall, and F1 score.
- Build and interpret confusion matrices.
- Use ROC curves and AUC.
- Validate models with cross-validation.
- Evaluate models when classes are imbalanced.

Outcome: an evaluation workflow that supports informed model selection and reliable performance reporting.

### [Module 5: Deploying Machine Learning Models](05-deployment/)

Turn a trained model into a web service that other applications can call.

In this module, you will:

- Serialize trained models.
- Expose predictions through a FastAPI service.
- Package the service with Docker.
- Deploy the service to a cloud platform.

Outcome: a containerized prediction service available through an API.

### [Module 6: Decision Trees and Ensemble Learning](06-trees/)

Train tree-based models and combine them into stronger predictive systems.

In this module, you will:

- Train and interpret decision trees.
- Build random forest models.
- Use gradient boosting with XGBoost.
- Tune model hyperparameters.
- Analyze feature importance.

Outcome: a tuned tree-based model selected through systematic evaluation.

## Task

This is what you need to do:

* Think of a problem that's interesting for you and find a dataset for that
* Describe this problem and explain how a model could be used
* Prepare the data and doing EDA, analyze important features
* Train multiple models, tune their performance and select the best model
* Export the notebook into a script
* Put your model into a web service and deploy it locally with Docker
* Bonus points for deploying the service to the cloud