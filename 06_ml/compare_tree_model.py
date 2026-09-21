from pathlib import Path

import numpy as np
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import make_scorer, precision_score, recall_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeClassifier


# ============================================================
# CONFIGURATION
# ============================================================

DATA_PATH = Path("data/curated/ml_customer_features.parquet")

TARGET = "repeat_purchase"

DROP_COLUMNS = [
    "customer_id",
    "last_purchase_date",
    TARGET,
]


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_parquet(DATA_PATH)

print("=" * 70)
print("DECISION TREE — 5-FOLD STRATIFIED CROSS-VALIDATION")
print("=" * 70)

print(f"\nDataset shape: {df.shape}")

X = df.drop(columns=DROP_COLUMNS)
y = df[TARGET]

categorical_features = [
    "country",
    "status",
]

numerical_features = [
    column
    for column in X.columns
    if column not in categorical_features
]

print(f"Feature matrix shape: {X.shape}")
print(f"Numerical features: {len(numerical_features)}")
print(f"Categorical features: {len(categorical_features)}")

print("\nTarget distribution:")
print(y.value_counts().sort_index())


# ============================================================
# PREPROCESSING
# ============================================================

numerical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median"),
        ),
    ]
)

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent"),
        ),
        (
            "onehot",
            OneHotEncoder(handle_unknown="ignore"),
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
# DECISION TREE
# ============================================================

model = DecisionTreeClassifier(
    max_depth=3,
    min_samples_leaf=5,
    random_state=42,
)

pipeline = Pipeline(
    steps=[
        (
            "preprocessor",
            preprocessor,
        ),
        (
            "model",
            model,
        ),
    ]
)


# ============================================================
# CROSS-VALIDATION
# ============================================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)

scoring = {
    "accuracy": "accuracy",
    "precision": make_scorer(
        precision_score,
        zero_division=0,
    ),
    "recall": make_scorer(
        recall_score,
        zero_division=0,
    ),
    "f1": make_scorer(
        f1_score,
        zero_division=0,
    ),
    "roc_auc": "roc_auc",
}

results = cross_validate(
    pipeline,
    X,
    y,
    cv=cv,
    scoring=scoring,
    return_train_score=False,
)


# ============================================================
# RESULTS
# ============================================================

print("\n5-fold stratified cross-validation:")
print("-" * 70)

for metric in scoring:
    scores = results[f"test_{metric}"]

    print(
        f"{metric.upper():<10} "
        f"scores = {np.round(scores, 4)}"
    )

    print(
        f"{'':10} "
        f"mean = {scores.mean():.4f}, "
        f"std = {scores.std():.4f}"
    )

print("\n" + "=" * 70)
print("END")
print("=" * 70)