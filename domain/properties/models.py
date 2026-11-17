from enum import Enum
from typing import List
from beanie import PydanticObjectId

from domain.common.models import Property
from repositories import Document


class PropertyDataType(str, Enum):
    DEFAULT = "default"


class Properties(Document):
    datasource_id: PydanticObjectId
    properties: List[Property]

    class Settings:
        name = "properties"
