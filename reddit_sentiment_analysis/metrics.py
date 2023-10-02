from prometheus_client import Histogram, Counter, Summary

OPENAI_PROMPT_TOKENS = Histogram(
    "openai_usage_prompt_tokens",
    "Used prompt tokens",
    buckets=[300, 1000]
)
OPENAI_COMPLETION_TOKENS = Histogram(
    "openai_usage_completion_tokens",
    "Used completion tokens",
    buckets=[20, 50, 100]
)

