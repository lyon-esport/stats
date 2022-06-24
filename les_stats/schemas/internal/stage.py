from pydantic import BaseModel


class Stage_Pydantic(BaseModel):
    name: str

    class Config:
        title = "Stage"
