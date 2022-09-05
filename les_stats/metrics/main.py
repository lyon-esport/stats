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
    from les_stats.models.tft.game import TFTGame
    from les_stats.models.valorant.game import ValorantGame

    metric_event.set(await Event.all().count())
    metric_tournament.set(await Tournament.all().count())
    metric_stage.set(await Stage.all().count())

    for game_type, games in [
        (RiotGame.tft, await TFTGame.all()),
        (RiotGame.tft, await TFTGame.all()),
        (RiotGame.tft, await TFTGame.all()),
    ]:
        for game in games:
            metric_game.labels(
                game_type,
                game.event if hasattr(game, "event") else None,
                game.tournament if hasattr(game, "tournament") else None,
                game.stage if hasattr(game, "stage") else None,
            ).set(await TFTGame.all().count())

    for game_type, games in [
        (RiotGame.valorant, await ValorantGame.all()),
        (RiotGame.valorant, await ValorantGame.all()),
        (RiotGame.valorant, await ValorantGame.all()),
    ]:
        pass
