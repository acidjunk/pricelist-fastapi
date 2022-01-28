from uuid import UUID

from server.crud.base import CRUDBase
from server.db.models import Order
from server.schemas.order import OrderCreate, OrderUpdate
from server.utils.json import json_dumps


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    def get_newest_order_id(self, *, shop_id: UUID) -> int:
        order_id = Order.query.filter_by(shop_id=str(shop_id)).count() + 1
        return order_id

    def get_order_by_shop_and_customer_order_id(self, *, customer_order_id: int, shop_id: UUID) -> Order:
        order = Order.query.filter_by(shop_id=shop_id).filter_by(customer_order_id=customer_order_id).first()
        return order


order_crud = CRUDOrder(Order)
