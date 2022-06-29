from prometheus_client import Counter, Gauge, Summary

from les_stats.models.internal.event import Event
from les_stats.models.internal.stage import Stage
from les_stats.models.internal.tournament import Tournament

metric_event = Gauge("les_stats_event_total", "number of event")
metric_tournament = Gauge("les_stats_event_tournament", "number of tournament")
metric_stage = Gauge("les_stats_event_stage", "number of stage")

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
metric_request_rate_limit_total_api = Counter(
    "les_stats_request_rate_limit_total", "number of API rate limit", ["client"]
)


async def init_metrics() -> None:
    metric_event.set(await Event.all().count())
    metric_tournament.set(await Tournament.all().count())
    metric_stage.set(await Stage.all().count())
