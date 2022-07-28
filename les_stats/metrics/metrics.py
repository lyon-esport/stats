from prometheus_client import Counter, Summary

metric_request_success_processing_seconds_api = Summary(
    "les_stats_request_success_processing_seconds",
    "time spent processing API request succeed",
    ["client"],
)
metric_request_failed_processing_seconds_api = Summary(
    "les_stats_request_failed_processing_seconds",
    "time spent processing API request failed",
    ["client"],
)
metric_request_http_code_total_api = Counter(
    "les_stats_request_http_code",
    "number of request per HTTP code",
    ["http_code", "game"],
)
