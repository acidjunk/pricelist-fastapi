from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel

from server.schemas.base import BoilerplateBaseModel
from server.types import JSON


class OrderItem(BaseModel):
    description: Optional[str]
    price: Optional[float]
    kind_id: Optional[str]
    kind_name: Optional[str]
    product_id: Optional[UUID]
    product_name: Optional[str]
    internal_product_id: Optional[str]
    quantity: Optional[int]


class OrderBase(BoilerplateBaseModel):
    shop_id: UUID
    table_id: Optional[UUID]  # Optional or required ?
    # order_info: List[OrderItem]
    order_info: List[OrderItem]
    total: Optional[float]
    customer_order_id: Optional[int]  # Optional or required ?


# Properties to receive via API on creation
class OrderCreate(OrderBase):
    pass


# Properties to receive via API on update
class OrderUpdate(OrderBase):
    pass


class OrderInDBBase(OrderBase):
    id: UUID
    created_at: datetime
    completed_at: Optional[datetime] = None
    completed_by: Optional[UUID]
    status: str

    class Config:
        orm_mode = True


# Additional properties to return via API
class OrderSchema(OrderInDBBase):
    table_name: str
    shop_name: Optional[str] = None
    completed_by_name: Optional[str]
