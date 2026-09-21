from pathlib import Path

import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    confusion_matrix,
    classification_report,
    roc_auc_score,
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import (
    OneHotEncoder,
    StandardScaler,
)


# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR
    / "data"
    / "curated"
    / "ml_customer_features.parquet"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_parquet(DATA_PATH)


# ============================================================
# FEATURES / TARGET
# ============================================================

TARGET = "repeat_purchase"

EXCLUDED_COLUMNS = [
    "customer_id",
    "last_purchase_date",
    TARGET,
]

FEATURE_COLUMNS = [
    column
    for column in df.columns
    if column not in EXCLUDED_COLUMNS
]

X = df[FEATURE_COLUMNS]

y = df[TARGET]


# ============================================================
# FEATURE TYPES
# ============================================================

categorical_features = [
    "country",
    "status",
]

numerical_features = [
    column
    for column in FEATURE_COLUMNS
    if column not in categorical_features
]


# ============================================================
# PREPROCESSING
# ============================================================

numerical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            ),
        ),
        (
            "scaler",
            StandardScaler(),
        ),
    ]
)


categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            ),
        ),
        (
            "onehot",
            OneHotEncoder(
                handle_unknown="ignore"
            ),
        ),
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        (
            "numerical",
            numerical_pipeline,
            numerical_features,
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features,
        ),
    ]
)


# ============================================================
# MODEL
# ============================================================

model = LogisticRegression(
    max_iter=2000,
    random_state=42,
)


pipeline = Pipeline(
    steps=[
        (
            "preprocessing",
            preprocessor,
        ),
        (
            "model",
            model,
        ),
    ]
)


# ============================================================
# FIT
# ============================================================

pipeline.fit(
    X,
    y,
)


# ============================================================
# PREDICTIONS
# ============================================================

predictions = pipeline.predict(X)

probabilities = pipeline.predict_proba(X)[:, 1]


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y,
    predictions,
)


print()
print("=" * 70)
print("LOGISTIC REGRESSION — TRAINING DATA DIAGNOSTIC")
print("=" * 70)

print("\nConfusion matrix:")
print(
    pd.DataFrame(
        cm,
        index=[
            "Actual 0",
            "Actual 1",
        ],
        columns=[
            "Predicted 0",
            "Predicted 1",
        ],
    )
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\nClassification report:")

print(
    classification_report(
        y,
        predictions,
        target_names=[
            "No future purchase",
            "Future purchase",
        ],
        zero_division=0,
    )
)


# ============================================================
# ROC-AUC
# ============================================================

print(
    "Training ROC-AUC:",
    round(
        roc_auc_score(
            y,
            probabilities,
        ),
        4,
    ),
)


# ============================================================
# INTERPRETATION
# ============================================================

print()
print("-" * 70)
print("IMPORTANT")
print("-" * 70)

print(
    """
These predictions were generated on the same observations
used to fit the model.

Therefore, these results are training-data diagnostics and
must NOT be interpreted as unseen-data performance.

The cross-validation results from train_model.py are the
primary model evaluation results.
"""
)

print("=" * 70)