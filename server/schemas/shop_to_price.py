from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ShopToPriceBase(BoilerplateBaseModel):
    active: bool
    new: bool
    price_id: UUID
    shop_id: UUID
    category_id: UUID
    kind_id: Optional[UUID] = None
    product_id: Optional[UUID] = None
    use_half: bool = False
    half: Optional[float] = None
    use_one: bool = False
    one: Optional[float] = None
    two_five: float = None
    use_two_five: bool = None
    use_five: bool = False
    five: Optional[float] = None
    use_joint: bool = False
    joint: Optional[float] = None
    use_piece: bool = False
    piece: Optional[float] = None


class ShopToPriceAvailability(BoilerplateBaseModel):
    active: bool


# Properties to receive via API on creation
class ShopToPriceCreate(ShopToPriceBase):

    pass


# Properties to receive via API on update
class ShopToPriceUpdate(ShopToPriceBase):
    pass


class ShopToPriceInDBBase(ShopToPriceBase):
    id: UUID
    created_at: datetime
    modified_at: datetime

    class Config:
        orm_mode = True


# Additional properties to return via API
class ShopToPriceSchema(ShopToPriceInDBBase):
    pass
