\# Week 3 Data Pipeline Design



\## Overview



The pipeline is a lightweight DAG-style data engineering workflow

that extracts raw e-commerce data, transforms it, loads curated

Parquet datasets, validates data quality, and updates the event

watermark after successful processing.



\## Pipeline Flow



```text

&#x20;                   ┌──────────────────────┐

&#x20;                   │      RAW DATA        │

&#x20;                   │                      │

&#x20;                   │ CSV + JSON files     │

&#x20;                   └──────────┬───────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌──────────────────────┐

&#x20;                   │       EXTRACT        │

&#x20;                   │                      │

&#x20;                   │ Full extraction for  │

&#x20;                   │ static datasets      │

&#x20;                   │                      │

&#x20;                   │ Watermark-based      │

&#x20;                   │ extraction for       │

&#x20;                   │ behavioral events    │

&#x20;                   └──────────┬───────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌──────────────────────┐

&#x20;                   │      TRANSFORM       │

&#x20;                   │                      │

&#x20;                   │ Column standardizing │

&#x20;                   │ Duplicate removal    │

&#x20;                   │ Type conversion      │

&#x20;                   │ Date conversion      │

&#x20;                   └──────────┬───────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌──────────────────────┐

&#x20;                   │        LOAD          │

&#x20;                   │                      │

&#x20;                   │ Curated Parquet      │

&#x20;                   │ datasets             │

&#x20;                   │                      │

&#x20;                   │ Events use           │

&#x20;                   │ idempotent loading   │

&#x20;                   └──────────┬───────────┘

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌──────────────────────┐

&#x20;                   │      VALIDATE        │

&#x20;                   │                      │

&#x20;                   │ Schema               │

&#x20;                   │ Completeness         │

&#x20;                   │ Uniqueness           │

&#x20;                   │ Range checks         │

&#x20;                   │ Referential integrity│

&#x20;                   └──────────┬───────────┘

&#x20;                              │

&#x20;                        Validation PASS

&#x20;                              │

&#x20;                              ▼

&#x20;                   ┌──────────────────────┐

&#x20;                   │   UPDATE WATERMARK   │

&#x20;                   │                      │

&#x20;                   │ Store latest         │

&#x20;                   │ successfully        │

&#x20;                   │ processed timestamp  │

&#x20;                   └──────────────────────┘





&#x20;             FAILURE / RETRY CONTROL



&#x20;       ┌─────────────────────────────────────┐

&#x20;       │          run\_pipeline.py            │

&#x20;       │                                     │

&#x20;       │ Run ID                              │

&#x20;       │ Task dependencies                   │

&#x20;       │ Retry handling                      │

&#x20;       │ Failure handling                    │

&#x20;       │ Pipeline logging                   │

&#x20;       └─────────────────────────────────────┘
