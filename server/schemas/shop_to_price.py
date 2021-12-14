from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ShopToPriceBase(BoilerplateBaseModel):
    id: Optional[UUID]
    active: Optional[bool]
    new: bool
    price_id: Optional[UUID]
    shop_id: Optional[UUID]
    category_id: Optional[UUID]
    kind_id: Optional[UUID]
    product_id: Optional[UUID]
    use_half: Optional[bool]
    half: Optional[float]
    use_one: Optional[bool]
    one: Optional[float]
    use_two_five: Optional[bool]
    two_five: Optional[float]
    use_five: Optional[bool]
    five: Optional[float]
    use_joint: Optional[bool]
    joint: Optional[float]
    use_piece: Optional[bool]
    piece: Optional[float]

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class ShopToPriceCreate(ShopToPriceBase):
    pass


# Properties to receive via API on update
class ShopToPriceUpdate(ShopToPriceBase):
    pass


class ShopToPriceInDBBase(ShopToPriceBase):
    created_at: Optional[datetime]
    modified_at: Optional[datetime]

    class Config:
        orm_mode = True


# Additional properties to return via API
class ShopToPriceSchema(ShopToPriceInDBBase):
    pass
