from pydantic import BaseModel


class TimeElapsed(BaseModel):
    second: int
    minute: int
    hour: int
    day: int
