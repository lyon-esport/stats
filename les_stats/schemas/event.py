from tortoise.contrib.pydantic import pydantic_model_creator

from les_stats.models.event import Event

Event_Pydantic = pydantic_model_creator(Event, name="Event")
EventIn_Pydantic = pydantic_model_creator(Event, name="EventIn", exclude_readonly=True)
