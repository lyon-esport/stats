from enum import Enum
from typing import Optional

from pydantic import BaseModel


class RiotHost(str, Enum):
    americas = "americas"
    asia = "asia"
    europe = "europe"
    sea = "sea"


class RiotGame(str, Enum):
    valorant = "valorant"
    lol = "lol"
    tft = "tft"


class GameSaveIn_Pydantic(BaseModel):
    event: Optional[str]
    tournament: Optional[str]
    stage: Optional[str]
    id: str

    class Config:
        title = "GameSaveIn"


class GameInPydantic(BaseModel):
    id: str
    region: str
