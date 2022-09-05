from prometheus_client import Gauge

metric_player_kills = Gauge(
    "les_stats_request_http_code",
    "number of request per HTTP code",
    ["http_code", "game"],
)
