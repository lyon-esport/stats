from tortoise.contrib.pydantic import pydantic_model_creator

from les_stats.models.stage import Stage

Stage_Pydantic = pydantic_model_creator(Stage, name="Stage")
StageIn_Pydantic = pydantic_model_creator(Stage, name="StageIn", exclude_readonly=True)
