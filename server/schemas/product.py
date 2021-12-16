from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class ProductBase(BoilerplateBaseModel):
    short_description_nl: str
    description_nl: str
    short_description_en: str
    description_en: str
    c: bool = False
    h: bool = False
    i: bool = False
    s: bool = False
    complete: bool = False
    approved_at: Optional[datetime] = None
    approved: bool = False
    approved_by: Optional[str] = None
    disapproved_reason: Optional[str] = None
    image_1: Optional[str] = None
    image_2: Optional[str] = None
    image_3: Optional[str] = None
    image_4: Optional[str] = None
    image_5: Optional[str] = None
    image_6: Optional[str] = None

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class ProductCreate(ProductBase):
    pass


# Properties to receive via API on update
class ProductUpdate(ProductBase):
    pass


class ProductInDBBase(ProductBase):
    id: UUID
    created_at: datetime
    modified_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class ProductSchema(ProductInDBBase):
    pass
