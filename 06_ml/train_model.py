from pathlib import Path
import joblib
import pandas as pd

from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate,
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

ARTIFACT_DIR = (
    BASE_DIR
    / "06_ml"
    / "artifacts"
)

MODEL_PATH = (
    ARTIFACT_DIR
    / "model_pipeline.joblib"
)


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_parquet(DATA_PATH)


print()
print("=" * 70)
print("WEEK 5 — LOGISTIC REGRESSION BASELINE")
print("=" * 70)


# ============================================================
# DEFINE FEATURES AND TARGET
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

X = df[FEATURE_COLUMNS].copy()

y = df[TARGET].copy()


# ============================================================
# IDENTIFY FEATURE TYPES
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
# DISPLAY DATASET INFORMATION
# ============================================================

print("\nDataset shape:")
print(df.shape)

print("\nFeature matrix shape:")
print(X.shape)

print("\nNumber of numerical features:")
print(len(numerical_features))

print("\nNumber of categorical features:")
print(len(categorical_features))

print("\nTarget distribution:")
print(y.value_counts().sort_index())


# ============================================================
# NUMERICAL PREPROCESSING
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


# ============================================================
# CATEGORICAL PREPROCESSING
# ============================================================

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


# ============================================================
# COMBINE PREPROCESSING
# ============================================================

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
# LOGISTIC REGRESSION MODEL
# ============================================================

model = LogisticRegression(
    max_iter=2000,
    random_state=42,
)


# ============================================================
# COMPLETE ML PIPELINE
# ============================================================

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
# STRATIFIED CROSS-VALIDATION
# ============================================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42,
)


# ============================================================
# EVALUATION METRICS
# ============================================================

scoring = {
    "accuracy": "accuracy",
    "precision": "precision",
    "recall": "recall",
    "f1": "f1",
    "roc_auc": "roc_auc",
}


# ============================================================
# CROSS-VALIDATION
# ============================================================

print()
print("-" * 70)
print("RUNNING 5-FOLD STRATIFIED CROSS-VALIDATION")
print("-" * 70)

cv_results = cross_validate(
    pipeline,
    X,
    y,
    cv=cv,
    scoring=scoring,
    return_train_score=False,
)


# ============================================================
# DISPLAY RESULTS
# ============================================================

print()
print("=" * 70)
print("CROSS-VALIDATION RESULTS")
print("=" * 70)

for metric in scoring:

    scores = cv_results[
        f"test_{metric}"
    ]

    print(
        f"\n{metric.upper()}:"
    )

    print(
        "  Fold scores:",
        [round(score, 4) for score in scores],
    )

    print(
        "  Mean:",
        round(scores.mean(), 4),
    )

    print(
        "  Std:",
        round(scores.std(), 4),
    )


# ============================================================
# FIT FINAL PIPELINE
# ============================================================

print()
print("-" * 70)
print("FITTING FINAL PIPELINE")
print("-" * 70)

pipeline.fit(
    X,
    y,
)
# ============================================================
# SAVE TRAINED MODEL PIPELINE
# ============================================================

ARTIFACT_DIR.mkdir(
    parents=True,
    exist_ok=True,
)

joblib.dump(
    pipeline,
    MODEL_PATH,
)

print()
print("Model pipeline saved to:")
print(MODEL_PATH)

# ============================================================
# PREDICTIONS ON FULL DATASET
# ============================================================

predictions = pipeline.predict(X)

probabilities = pipeline.predict_proba(X)[:, 1]


print()
print("-" * 70)
print("FULL-DATASET FIT SUMMARY")
print("-" * 70)

print(
    "\nAccuracy:",
    round(
        accuracy_score(
            y,
            predictions,
        ),
        4,
    ),
)

print(
    "Precision:",
    round(
        precision_score(
            y,
            predictions,
            zero_division=0,
        ),
        4,
    ),
)

print(
    "Recall:",
    round(
        recall_score(
            y,
            predictions,
            zero_division=0,
        ),
        4,
    ),
)

print(
    "F1:",
    round(
        f1_score(
            y,
            predictions,
            zero_division=0,
        ),
        4,
    ),
)

print(
    "ROC-AUC:",
    round(
        roc_auc_score(
            y,
            probabilities,
        ),
        4,
    ),
)


# ============================================================
# MODEL PREDICTION EXAMPLES
# ============================================================

results = df[
    [
        "customer_id",
        "repeat_purchase",
    ]
].copy()

results["predicted_purchase"] = predictions

results["purchase_probability"] = probabilities

results = results.sort_values(
    "purchase_probability",
    ascending=False,
)


print()
print("-" * 70)
print("TOP CUSTOMER PURCHASE PROBABILITIES")
print("-" * 70)

print(
    results.head(10).to_string(
        index=False
    )
)


# ============================================================
# SAVE PREDICTIONS
# ============================================================

output_path = (
    BASE_DIR
    / "data"
    / "curated"
    / "ml_predictions.parquet"
)

results.to_parquet(
    output_path,
    index=False,
)


print()
print("Predictions saved to:")
print(output_path)

print()
print("=" * 70)
print("MODEL TRAINING COMPLETE")
print("=" * 70)