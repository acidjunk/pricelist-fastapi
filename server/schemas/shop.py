from datetime import datetime
from typing import List, Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ShopBase(BoilerplateBaseModel):
    name: str
    description: str


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


class ShopWithPrices(ShopInDBBase):
    prices: List[dict]


class ShopCacheStatus(ShopInDBBase):
    modified_at: Optional[datetime]
