from pathlib import Path

import pandas as pd


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
# LOAD ML DATASET
# ============================================================

df = pd.read_parquet(DATA_PATH)


print()
print("=" * 70)
print("WEEK 5 ML FEATURE AUDIT")
print("=" * 70)


# ============================================================
# BASIC DATASET INFORMATION
# ============================================================

print("\nDataset shape:")
print(df.shape)

print("\nNumber of unique customers:")
print(df["customer_id"].nunique())

print("\nNumber of duplicate rows:")
print(df.duplicated().sum())


# ============================================================
# TARGET DISTRIBUTION
# ============================================================

print("\n" + "-" * 70)
print("TARGET DISTRIBUTION")
print("-" * 70)

target_counts = (
    df["repeat_purchase"]
    .value_counts()
    .sort_index()
)

print(target_counts)

print("\nTarget percentages:")

target_percentages = (
    df["repeat_purchase"]
    .value_counts(normalize=True)
    .sort_index()
    .mul(100)
    .round(2)
)

print(target_percentages)


# ============================================================
# FEATURE TYPES
# ============================================================

print("\n" + "-" * 70)
print("FEATURE DATA TYPES")
print("-" * 70)

print(df.dtypes)


# ============================================================
# MISSING VALUES
# ============================================================

print("\n" + "-" * 70)
print("MISSING VALUES")
print("-" * 70)

missing = df.isna().sum()

print(
    missing[missing > 0]
)


# ============================================================
# NUMERICAL FEATURE SUMMARY
# ============================================================

print("\n" + "-" * 70)
print("NUMERICAL FEATURE SUMMARY")
print("-" * 70)

numeric_columns = df.select_dtypes(
    include="number"
).columns

print(
    df[numeric_columns]
    .describe()
    .T
    .round(2)
)


# ============================================================
# UNIQUE VALUES
# ============================================================

print("\n" + "-" * 70)
print("UNIQUE VALUES PER COLUMN")
print("-" * 70)

for column in df.columns:

    print(
        f"{column}: "
        f"{df[column].nunique(dropna=False)} unique values"
    )


# ============================================================
# CATEGORICAL DISTRIBUTIONS
# ============================================================

print("\n" + "-" * 70)
print("CATEGORICAL FEATURE DISTRIBUTIONS")
print("-" * 70)

for column in ["country", "status"]:

    print(f"\n{column}:")

    print(
        df[column]
        .value_counts(dropna=False)
    )


# ============================================================
# PREVIOUS PURCHASE VS TARGET
# ============================================================

print("\n" + "-" * 70)
print("PREVIOUS PURCHASE VS TARGET")
print("-" * 70)

print(
    pd.crosstab(
        df["has_previous_purchase"],
        df["repeat_purchase"],
        margins=True,
    )
)


# ============================================================
# FEATURE MEANS BY TARGET
# ============================================================

print("\n" + "-" * 70)
print("NUMERICAL FEATURE MEANS BY TARGET")
print("-" * 70)

feature_means = (
    df.groupby("repeat_purchase")[numeric_columns]
    .mean()
    .T
    .round(2)
)

print(feature_means)


# ============================================================
# ZERO-VARIANCE FEATURES
# ============================================================

print("\n" + "-" * 70)
print("ZERO-VARIANCE FEATURES")
print("-" * 70)

zero_variance = []

for column in numeric_columns:

    if df[column].nunique(dropna=True) <= 1:
        zero_variance.append(column)

if zero_variance:

    for column in zero_variance:
        print(column)

else:

    print("None")


# ============================================================
# FINAL CHECK
# ============================================================

print("\n" + "=" * 70)
print("FEATURE AUDIT COMPLETE")
print("=" * 70)

print(
    "\nDataset ready for the next validation stage."
)

print()