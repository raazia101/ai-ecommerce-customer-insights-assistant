CREATE SCHEMA IF NOT EXISTS ml;

CREATE TABLE IF NOT EXISTS ml.predictions (
    prediction_id BIGSERIAL PRIMARY KEY,
    customer_id TEXT NOT NULL,
    model_version TEXT NOT NULL,
    prediction SMALLINT NOT NULL CHECK (prediction IN (0, 1)),
    probability DOUBLE PRECISION NOT NULL CHECK (probability >= 0 AND probability <= 1),
    scored_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,

    CONSTRAINT uq_ml_predictions_customer_model
        UNIQUE (customer_id, model_version)
);
