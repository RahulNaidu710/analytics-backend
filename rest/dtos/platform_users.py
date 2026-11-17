from typing import List, Optional

from beanie import PydanticObjectId
from pydantic import BaseModel

from domain.platform_users.models import PlatformUser

from .model_response import ModelResponse


class PrivateUserResponse(PlatformUser, ModelResponse):
    pass


class PlatformUserResponse(ModelResponse):
    id: PydanticObjectId
    first_name: str
    last_name: str
    email: str
    picture: Optional[str]
    slack_channel: Optional[str]
    has_visited_sheets: Optional[bool]

    class Config:
        allow_population_by_field_name = True
        orm_mode = True


class PlatformUserWithPrivateFields(PlatformUserResponse):
    api_key: Optional[str]
    sheet_token: Optional[str]


class CreateUserDto(BaseModel):
    first_name: str
    last_name: str
    email: str
    password: str


class ResetPasswordDto(BaseModel):
    email: str
    password: str


class AppWiseUserDto(BaseModel):
    app: PydanticObjectId
    users: List[PlatformUserResponse]
