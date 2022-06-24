from typing import List, Optional

from pydantic import BaseModel

from les_stats.schemas.internal.stage import Stage_Pydantic


class Tournament_Pydantic(BaseModel):
    name: str
    stages: Optional[List[Stage_Pydantic]]

    class Config:
        title = "Tournament"


class TournamentIn_Pydantic(BaseModel):
    stages: Optional[List[Stage_Pydantic]]

    class Config:
        title = "TournamentIn"
