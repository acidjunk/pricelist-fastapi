from typing import Optional
from uuid import UUID
from datetime import datetime
from server.schemas.base import BoilerplateBaseModel


class PriceBase(BoilerplateBaseModel):
    id: Optional[UUID]
    # Int or string ? In shops.get_multi() is int in prices.get_multi() is str
    internal_product_id: str
    half: Optional[float]
    one: Optional[float]
    two_five: Optional[float]
    five: Optional[float]
    joint: Optional[float]
    piece: Optional[float]

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class PriceCreate(PriceBase):
    pass


# Properties to receive via API on update
class PriceUpdate(PriceBase):
    pass


class PriceInDBBase(PriceBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class PriceSchema(PriceInDBBase):
    pass
