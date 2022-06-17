LoL statistics

[![PyPI](https://img.shields.io/pypi/v/les-stats.svg)](https://pypi.python.org/pypi/les-stats)
[![PyPI versions](https://img.shields.io/pypi/pyversions/les-stats.svg)](https://pypi.python.org/pypi/les-stats)
[![Python test](https://github.com/lyon-esport/stats/actions/workflows/test.yml/badge.svg)](https://github.com/lyon-esport/stats/actions/workflows/test.yml)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/ambv/black)

# Install
```
pip install les-stats
```

# Dev
Install [Poetry](https://python-poetry.org/docs/master/#installing-with-the-official-installer) with version >= 1.2.0a1

Install and setup dependencies
```
poetry install
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
Create an `.env` file with this content
```
DB_URL="Your db url following https://tortoise.github.io/databases.html"
VALORANT_API_KEY="valorant api key"
VALORANT_API_ROUTING="euw1"

Optional:
EXPORTER_PORT="your port (default 9345)"
BACKEND_CORS_ORIGINS="[http://localhost.fr,http://test.localhost.fr]"
SENTRY_DSN="your sentry DSN"
```

Start the app
```
uvicorn les_lol_stats.main:app --reload
```

# API
APIs documentation are available at http://127.0.0.1:8000/docs

# Prometheus
Stats are available at http://127.0.0.1:9345/metrics

# Licence

The code is under CeCILL license.

You can find all details here: https://cecill.info/licences/Licence_CeCILL_V2.1-en.html

# Credits

Copyright © Ludovic Ortega, 2022

Contributor(s):

-Ortega Ludovic - ludovic.ortega@lyon-esport.fr
