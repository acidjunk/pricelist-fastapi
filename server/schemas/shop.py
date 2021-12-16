from datetime import datetime
from typing import List, Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ShopBase(BoilerplateBaseModel):
    name: str
    description: str

    class Config:
        orm_mode = True


class ShopWithPrices(ShopBase):
    prices: List[dict]


class ShopCacheStatus(BoilerplateBaseModel):
    modified_at: Optional[datetime]

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class ShopCreate(ShopBase):
    pass


# Properties to receive via API on update
class ShopUpdate(ShopBase):
    pass


class ShopInDBBase(ShopBase):
    id: UUID

    class Config:
        orm_mode = True


# Additional properties to return via API
class ShopSchema(ShopInDBBase):
    pass
