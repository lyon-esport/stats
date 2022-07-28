from les_stats.metrics.internal.metrics import (
    metric_event,
    metric_game,
    metric_stage,
    metric_tournament,
)


async def init_metrics() -> None:
    from les_stats.client_api.riot import RiotGame
    from les_stats.models.internal.event import Event
    from les_stats.models.internal.stage import Stage
    from les_stats.models.internal.tournament import Tournament
    from les_stats.models.lol.game import LOLGame
    from les_stats.models.tft.game import TFTGame
    from les_stats.models.valorant.game import ValorantGame

    metric_event.set(await Event.all().count())
    metric_tournament.set(await Tournament.all().count())
    metric_stage.set(await Stage.all().count())
    metric_game.labels(RiotGame.tft).set(await TFTGame.all().count())
    metric_game.labels(RiotGame.valorant).set(await ValorantGame.all().count())
    metric_game.labels(RiotGame.lol).set(await LOLGame.all().count())
