from server.crud.base import CRUDBase
from server.db.models import Order
from server.schemas.order import OrderCreate, OrderUpdate


class CRUDOrder(CRUDBase[Order, OrderCreate, OrderUpdate]):
    pass


order_crud = CRUDOrder(Order)
