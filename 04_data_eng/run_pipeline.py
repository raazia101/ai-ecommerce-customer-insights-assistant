import importlib.util
from datetime import datetime
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CURATED_DIR = DATA_DIR / "curated"
PIPELINE_LOG = DATA_DIR / "pipeline_log.csv"


def load_module(module_name: str, file_path: Path):
    """Load a Python module from a file path."""

    spec = importlib.util.spec_from_file_location(
        module_name,
        file_path,
    )

    module = importlib.util.module_from_spec(spec)

    spec.loader.exec_module(module)

    return module


def log_pipeline_event(
    run_id: str,
    task_name: str,
    attempt: int,
    status: str,
    error: str = "",
) -> None:
    """Append a pipeline execution event to the log."""

    log_entry = pd.DataFrame(
        [
            {
                "timestamp": datetime.now().isoformat(),
                "run_id": run_id,
                "task": task_name,
                "attempt": attempt,
                "status": status,
                "error": error,
            }
        ]
    )

    if PIPELINE_LOG.exists():
        log_entry.to_csv(
            PIPELINE_LOG,
            mode="a",
            header=False,
            index=False,
        )
    else:
        log_entry.to_csv(
            PIPELINE_LOG,
            index=False,
        )


def run_task(
    run_id: str,
    task_name: str,
    task_function,
    retries: int = 2,
) -> bool:
    """
    Run a pipeline task with retry handling.

    Returns True when the task succeeds.
    Returns False after all retry attempts fail.
    """

    for attempt in range(1, retries + 2):
        try:
            print(
                f"\n[{task_name}] "
                f"Attempt {attempt}"
            )

            log_pipeline_event(
                run_id,
                task_name,
                attempt,
                "STARTED",
            )

            task_function()

            print(
                f"[{task_name}] "
                f"SUCCESS"
            )

            log_pipeline_event(
                run_id,
                task_name,
                attempt,
                "SUCCESS",
            )

            return True

        except Exception as error:
            print(
                f"[{task_name}] "
                f"FAILED: {error}"
            )

            log_pipeline_event(
                run_id,
                task_name,
                attempt,
                "FAILED",
                str(error),
            )

            if attempt <= retries:
                print(
                    f"[{task_name}] "
                    f"Retrying..."
                )

            else:
                print(
                    f"[{task_name}] "
                    f"All retry attempts failed."
                )

    return False


def run_pipeline() -> bool:
    """Run the complete data engineering pipeline."""

    run_id = datetime.now().strftime(
        "RUN-%Y%m%d-%H%M%S"
    )

    print("=" * 60)
    print(f"Starting pipeline: {run_id}")
    print("=" * 60)

    log_pipeline_event(
        run_id,
        "PIPELINE",
        0,
        "STARTED",
    )

    extract = load_module(
        "extract",
        BASE_DIR / "04_data_eng" / "extract.py",
    )

    transform = load_module(
        "transform",
        BASE_DIR / "04_data_eng" / "transform.py",
    )

    validate = load_module(
        "validate",
        BASE_DIR / "04_data_eng" / "validate_data.py",
    )

    load = load_module(
        "load",
        BASE_DIR / "04_data_eng" / "load.py",
    )

    pipeline_data = {}

    # ---------------------------------------------------------
    # TASK 1: EXTRACT
    # ---------------------------------------------------------

    def extract_task():
        """Extract all raw datasets."""

        pipeline_data["customers"] = extract.extract_csv(
            "customers.csv"
        )

        pipeline_data["products"] = extract.extract_csv(
            "products.csv"
        )

        pipeline_data["orders"] = extract.extract_csv(
            "orders.csv"
        )

        pipeline_data["order_items"] = extract.extract_csv(
            "order_items.csv"
        )

        pipeline_data["transactions"] = extract.extract_csv(
            "transactions.csv"
        )

        pipeline_data["events"] = (
            extract.extract_incremental_events()
        )

    if not run_task(
        run_id,
        "EXTRACT",
        extract_task,
    ):
        log_pipeline_event(
            run_id,
            "PIPELINE",
            0,
            "FAILED",
            "Pipeline stopped at EXTRACT.",
        )

        print(
            "\nPipeline stopped at EXTRACT."
        )

        return False

    # ---------------------------------------------------------
    # TASK 2: TRANSFORM
    # ---------------------------------------------------------

    def transform_task():
        """Transform all extracted datasets."""

        pipeline_data["customers"] = (
            transform.clean_customers(
                pipeline_data["customers"]
            )
        )

        pipeline_data["products"] = (
            transform.clean_products(
                pipeline_data["products"]
            )
        )

        pipeline_data["orders"] = (
            transform.clean_orders(
                pipeline_data["orders"]
            )
        )

        pipeline_data["order_items"] = (
            transform.clean_order_items(
                pipeline_data["order_items"]
            )
        )

        pipeline_data["transactions"] = (
            transform.clean_transactions(
                pipeline_data["transactions"]
            )
        )

        pipeline_data["events"] = (
            transform.clean_events(
                pipeline_data["events"]
            )
        )

    if not run_task(
        run_id,
        "TRANSFORM",
        transform_task,
    ):
        log_pipeline_event(
            run_id,
            "PIPELINE",
            0,
            "FAILED",
            "Pipeline stopped at TRANSFORM.",
        )

        print(
            "\nPipeline stopped at TRANSFORM."
        )

        return False

    # ---------------------------------------------------------
    # TASK 3: LOAD
    # ---------------------------------------------------------

    def load_task():
        """Load transformed data into the curated layer."""

        load.load_parquet(
            pipeline_data["customers"],
            "customers.parquet",
        )

        load.load_parquet(
            pipeline_data["products"],
            "products.parquet",
        )

        load.load_parquet(
            pipeline_data["orders"],
            "orders.parquet",
        )

        load.load_parquet(
            pipeline_data["order_items"],
            "order_items.parquet",
        )

        load.load_parquet(
            pipeline_data["transactions"],
            "transactions.parquet",
        )

        events = pd.DataFrame(
            pipeline_data["events"]
        )

        if not events.empty:
            load.load_incremental_parquet(
                events,
                "events.parquet",
                "event_id",
            )
        else:
            print(
                "No new events to load."
            )

    if not run_task(
        run_id,
        "LOAD",
        load_task,
    ):
        log_pipeline_event(
            run_id,
            "PIPELINE",
            0,
            "FAILED",
            "Pipeline stopped at LOAD.",
        )

        print(
            "\nPipeline stopped at LOAD."
        )

        return False

    # ---------------------------------------------------------
    # TASK 4: VALIDATE
    # ---------------------------------------------------------

    validation_result = False

    def validate_task():
        """Validate the curated datasets."""

        nonlocal validation_result

        validation_result = (
            validate.run_validations()
        )

        if not validation_result:
            raise RuntimeError(
                "Data validation failed."
            )

    if not run_task(
        run_id,
        "VALIDATE",
        validate_task,
    ):
        log_pipeline_event(
            run_id,
            "PIPELINE",
            0,
            "FAILED",
            "Pipeline stopped at VALIDATE.",
        )

        print(
            "\nPipeline stopped at VALIDATE."
        )

        return False

    # ---------------------------------------------------------
    # TASK 5: UPDATE WATERMARK
    # ---------------------------------------------------------

    def watermark_task():
        """Update the event watermark after successful validation."""

        events_path = (
            CURATED_DIR / "events.parquet"
        )

        events = pd.read_parquet(
            events_path
        )

        if events.empty:
            print(
                "No events available. "
                "Watermark not updated."
            )
            return

        latest_timestamp = events[
            "timestamp"
        ].max()

        extract.save_watermark(
            latest_timestamp.to_pydatetime()
        )

        print(
            "Watermark updated to:",
            latest_timestamp,
        )

    if not run_task(
        run_id,
        "WATERMARK",
        watermark_task,
    ):
        log_pipeline_event(
            run_id,
            "PIPELINE",
            0,
            "FAILED",
            "Pipeline stopped at WATERMARK.",
        )

        print(
            "\nPipeline stopped at WATERMARK."
        )

        return False

    # ---------------------------------------------------------
    # PIPELINE COMPLETE
    # ---------------------------------------------------------

    log_pipeline_event(
        run_id,
        "PIPELINE",
        0,
        "SUCCESS",
    )

    print("\n" + "=" * 60)
    print(
        f"Pipeline {run_id} "
        f"completed successfully."
    )
    print("=" * 60)

    return True


if __name__ == "__main__":
    run_pipeline()