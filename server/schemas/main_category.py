from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class MainCategoryBase(BoilerplateBaseModel):
    name: str


# Properties to receive via API on creation
class MainCategoryCreate(MainCategoryBase):
    pass


# Properties to receive via API on update
class MainCategoryUpdate(MainCategoryBase):
    pass


class MainCategoryInDBBase(MainCategoryBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class MainCategorySchema(MainCategoryInDBBase):
    pass
