from tortoise.contrib.pydantic import pydantic_model_creator

from les_stats.models.tournament import Tournament

Tournament_Pydantic = pydantic_model_creator(Tournament, name="Tournament")
TournamentIn_Pydantic = pydantic_model_creator(Tournament, name="TournamentIn", exclude_readonly=True)
