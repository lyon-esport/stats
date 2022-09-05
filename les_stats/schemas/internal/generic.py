from pydantic import BaseModel


class GameTimeElapsed(BaseModel):
    second: int
    minute: int
    hour: int
    day: int
