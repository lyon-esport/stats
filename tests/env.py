import os

os.environ["LES_STATS_DB_URL"] = "sqlite://:memory:"
os.environ["LES_STATS_SALT"] = "salt"
os.environ["LES_STATS_VALORANT_API_KEY"] = "API_KEY"
os.environ["LES_STATS_VALORANT_API_ROUTING"] = "API_ROUTING"
os.environ["LES_STATS_LOL_API_KEY"] = "API_KEY"
os.environ["LES_STATS_LOL_API_ROUTING"] = "API_ROUTING"
os.environ["LES_STATS_TFT_API_KEY"] = "API_KEY"
os.environ["LES_STATS_TFT_API_ROUTING"] = "API_ROUTING"
