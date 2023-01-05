import os

os.environ["LES_STATS_DB_URL"] = "sqlite://:memory:"
os.environ["LES_STATS_TIMEZONE"] = "Europe/Paris"
os.environ["LES_STATS_SALT"] = "salt"
os.environ["LES_STATS_VALORANT_API_KEY"] = "API_KEY"
os.environ["LES_STATS_VALORANT_API_ROUTING"] = "euw1"
os.environ["LES_STATS_TFT_API_KEY"] = "API_KEY"
os.environ["LES_STATS_TFT_API_ROUTING"] = "euw1"
os.environ["LES_STATS_LOL_API_KEY"] = "API_KEY"
os.environ["LES_STATS_LOL_API_ROUTING"] = "euw1"
