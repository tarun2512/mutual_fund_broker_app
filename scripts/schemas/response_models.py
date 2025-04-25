from typing import Any, Optional

from pydantic import BaseModel


class DefaultResponse(BaseModel):
    status: str = "failed"
    message: Optional[str]
    data: Optional[Any] = {}


class DefaultFailureResponse(DefaultResponse):
    message: Optional[str] = ""
    error: Optional[Any] = ""


class DefaultSuccessResponse(DefaultResponse):
    status: str = "success"
    message: Optional[str] = ""
    data: Optional[Any] = {}
