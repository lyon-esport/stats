from prometheus_client import Gauge

metric_event = Gauge("les_stats_event_total", "number of event")
metric_tournament = Gauge("les_stats_tournament_total", "number of tournament")
metric_stage = Gauge("les_stats_stage_total", "number of stage")
metric_game = Gauge(
    "les_stats_game",
    "number of game registered in system",
    ["game", "event", "tournament", "stage"],
)
