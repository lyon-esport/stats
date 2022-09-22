# coding=utf-8
# author Etienne G.

import logging
import os

from pyot.conf.model import ModelConf, activate_model
from pyot.conf.pipeline import PipelineConf, activate_pipeline

logger = logging.getLogger(__name__)


@activate_model("val")
class ValModel(ModelConf):
    default_platform = "eu"
    default_region = "europe"
    default_version = "latest"
    default_locale = "fr_fr"


@activate_model("riot")
class RiotModel(ModelConf):
    default_platform = "eu"
    default_region = "europe"
    default_version = "latest"
    default_locale = "fr_fr"


@activate_pipeline("val")
class ValPipeline(PipelineConf):
    name = "val"
    default = True
    stores = [
        {
            "backend": "pyot.stores.diskcache.DiskCache",
            "directory": "./cache",
            "expirations": {
                "account_v1_by_riot_id": 31 * 24 * 3600,
                "account_v1_by_puuid": 31 * 24 * 3600,
                "content_v1_contents": 3600,
                "match_v1_matchlist": 600,
                "match_v1_match": 600,
            },
        },
        # {
        #     "backend": "pyot.stores.cdragon.CDragon",
        # },
        {
            "backend": "pyot.stores.riotapi.RiotAPI",
            "api_key": os.environ["LES_STATS_VALORANT_API_KEY"],
        },
    ]
