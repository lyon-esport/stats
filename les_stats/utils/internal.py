from typing import Dict


def generate_kwargs_structure(
    event: str = None, tournament: str = None, stage: str = None, prefix=""
) -> Dict[str, str]:
    filters = {}

    if event is not None:
        filters[f"{prefix}event"] = event

    if tournament is not None:
        filters[f"{prefix}tournament"] = tournament

    if stage is not None:
        filters[f"{prefix}stage"] = stage

    return filters
