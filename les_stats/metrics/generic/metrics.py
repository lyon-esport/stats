from prometheus_client import Gauge

metric_player_wins = Gauge(
    "les_stats_player_wins",
    "number of wins for a player in a game",
    ["event", "tournament", "stage", "game", "player_id", "player_name"],
)

metric_player_defeats = Gauge(
    "les_stats_player_defeats",
    "number of defeats for a player in a game",
    ["event", "tournament", "stage", "game", "player_id", "player_name"],
)

metric_player_time_played = Gauge(
    "les_stats_player_time_played",
    "number of seconds played for a player in a game",
    ["event", "tournament", "stage", "game", "player_id", "player_name"],
)

metric_player_kills = Gauge(
    "les_stats_player_kills",
    "number of kills for a player in a game",
    ["event", "tournament", "stage", "game", "player_id", "player_name"],
)

metric_player_assists = Gauge(
    "les_stats_player_assists",
    "number of assists for a player in a game",
    ["event", "tournament", "stage", "game", "player_id", "player_name"],
)

metric_player_deaths = Gauge(
    "les_stats_player_deaths",
    "number of deaths for a player in a game",
    ["event", "tournament", "stage", "game", "player_id", "player_name"],
)

metric_player_damages_given = Gauge(
    "les_stats_player_damages_given",
    "number of dammages given by a player in a game",
    ["event", "tournament", "stage", "game", "player_id", "player_name"],
)

metric_player_damages_received = Gauge(
    "les_stats_player_damages_received",
    "number of dammages received by a player in a game",
    ["event", "tournament", "stage", "game", "player_id", "player_name"],
)
