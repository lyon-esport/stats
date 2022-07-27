from typing import Any

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    status_code: int
    message: Any


class DataResponse(BaseModel):
    data: Any = None
    error: ErrorResponse = None
