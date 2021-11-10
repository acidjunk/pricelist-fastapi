from typing import Optional
from uuid import UUID
from datetime import datetime
from server.schemas.base import BoilerplateBaseModel


class CategoryBase(BoilerplateBaseModel):
    id: UUID
    name: str
    shop_id: str
    image_1: dict
    image_2: dict

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class CategoryCreate(CategoryBase):
    pass


# Properties to receive via API on update
class CategoryUpdate(CategoryBase):
    pass


class CategoryInDBBase(CategoryBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class CategorySchema(CategoryInDBBase):
    pass
