Statistics for various games (save game in system and filter statistics based on Event, Tournament or Stage)

[![PyPI](https://img.shields.io/pypi/v/les-stats.svg)](https://pypi.python.org/pypi/les-stats)
[![PyPI versions](https://img.shields.io/pypi/pyversions/les-stats.svg)](https://pypi.python.org/pypi/les-stats)
[![Python test](https://github.com/lyon-esport/stats/actions/workflows/test.yml/badge.svg)](https://github.com/lyon-esport/stats/actions/workflows/test.yml)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Games supported
- TFT
- Valorant (work in progress)
- LoL (work in progress)

# Install
```bash
pip install les-stats
```

# Dev
Install [Poetry](https://python-poetry.org/docs/master/#installing-with-the-official-installer)

Install and setup dependencies
```
poetry install --with dev
poetry shell
pre-commit install
```

### Run unit test
```
pytest
```

### Run pre-commit
```
pre-commit run --all-files
```

# Run
Create an `.env` file with this content or create environment variables
```
LES_STATS_TIMEZONE="TZ database name following https://en.wikipedia.org/wiki/List_of_tz_database_time_zones"
LES_STATS_DB_URL="Your db url following https://tortoise.github.io/databases.html"
LES_STATS_SALT="Salt used to hash API key of internal app"

Optional:
LES_STATS_TFT_API_KEY="tft api key"
LES_STATS_TFT_API_ROUTING="tft api routing"
LES_STATS_VALORANT_API_KEY="valorant api key"
LES_STATS_VALORANT_API_ROUTING="valorant api routing"
LES_STATS_LOL_API_KEY="lol api key"
LES_STATS_LOL_API_ROUTING="lol api routing"
LES_STATS_APP_HOST="Application bind sotcket to this host (default localhost)"
LES_STATS_APP_PORT="Application bind sotcket with this port (default 8000)"
LES_STATS_EXPORTER_ADDR="Exporter bind sotcket to this host (default localhost)"
LES_STATS_EXPORTER_PORT="Exporter bind sotcket with this port (default 9345)"
LES_STATS_BACKEND_CORS_ORIGINS="[http://localhost.fr,http://test.localhost.fr]"
LES_STATS_SENTRY_DSN="your sentry DSN"
```

Start the app
```
python3 -m les_stats.main
```

Manage API Key
```
python3 -m les_stats.utils.auth --help
```

Import matches
```
python3 -m les_stats.utils.import_match --help
```

# API
APIs documentation are available at http://<LES_STATS_APP_HOST>:<LES_STATS_APP_PORT>/docs

# Prometheus
Stats are available at http://<LES_STATS_EXPORTER_ADDR>:<LES_STATS_EXPORTER_PORT>/metrics (work in progess)

# Licence

The code is under CeCILL license.

You can find all details here: https://cecill.info/licences/Licence_CeCILL_V2.1-en.html

# Credits

Copyright © Ludovic Ortega, 2022

Contributor(s):

-Ortega Ludovic - ludovic.ortega@lyon-esport.fr
