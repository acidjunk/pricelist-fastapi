from datetime import datetime
from typing import List, Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel
from server.types import JSON


class OrderItem(BoilerplateBaseModel):
    description: Optional[str]
    price: Optional[str]
    kind_id: Optional[str]
    kind_name: Optional[str]
    product_id: Optional[str]
    product_name: Optional[str]
    internal_product_id: Optional[str]
    quantity: int


class OrderBase(BoilerplateBaseModel):
    shop_id: UUID
    shop_name: Optional[str] = None
    order_info: List[OrderItem]
    total: Optional[float]
    customer_order_id: int
    status: str
    completed_by: Optional[UUID]
    completed_by_name: Optional[str]
    table_id: UUID
    table_name: str


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

    class Config:
        orm_mode = True


# Additional properties to return via API
class OrderSchema(OrderInDBBase):
    pass
