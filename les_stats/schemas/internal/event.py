from typing import List, Optional

from pydantic import BaseModel

from les_stats.schemas.internal.tournament import Tournament_Pydantic


class Event_Pydantic(BaseModel):
    name: str
    tournaments: Optional[List[Tournament_Pydantic]]

    class Config:
        title = "Event"


class EventIn_Pydantic(BaseModel):
    tournaments: Optional[List[Tournament_Pydantic]]

    class Config:
        title = "EventIn"
