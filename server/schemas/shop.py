from uuid import UUID
from datetime import datetime
from server.schemas.base import BoilerplateBaseModel


class ShopBase(BoilerplateBaseModel):
    id: UUID
    name: str
    description: str

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class ShopCreate(ShopBase):
    pass


# Properties to receive via API on update
class ShopUpdate(ShopBase):
    pass


class ShopInDBBase(ShopBase):

    class Config:
        orm_mode = True


# Additional properties to return via API
class ShopSchema(ShopInDBBase):
    pass