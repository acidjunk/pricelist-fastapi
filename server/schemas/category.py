from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class CategoryBase(BoilerplateBaseModel):
    id: UUID
    shop_id: str
    main_category_id: str
    name: str
    name_en: Optional[str] = None
    description: str
    icon: Optional[str] = None
    order_number: int = 0
    cannabis: bool = False
    image_1: str
    image_2: str

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class CategoryCreate(CategoryBase):
    pass


# Properties to receive via API on update
class CategoryUpdate(CategoryBase):
    pass


class CategoryInDBBase(CategoryBase):
    created_at: datetime
    modified_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class CategorySchema(CategoryInDBBase):
    pass
