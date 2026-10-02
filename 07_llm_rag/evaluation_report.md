# Prompt Evaluation Report

## Evaluation Dimensions

The Week 7 prompt evaluation considers:

- Correctness
- Groundedness
- Completeness
- Format compliance
- Latency
- Cost

## Deterministic Checks

The following checks can be automated:

### Correctness
Does the predicted customer segment match the expected result?

### Format compliance
Does the response contain valid JSON with all required fields?

### Schema validity
Are all values of the correct type and within allowed ranges?

## Human Review

Human evaluation can additionally assess:

- Whether the summary accurately represents the supplied information
- Whether important information was omitted
- Whether the response contains unsupported claims

## Limitations

Because no hosted LLM API credentials are configured, this evaluation
dataset currently provides the fixed test structure and deterministic
validation criteria rather than live model scores.

Live model evaluation can be added once an API configuration is available.