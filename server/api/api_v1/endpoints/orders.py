from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api import deps
from server.api.api_v1.router_fix import APIRouter
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_order import order_crud
from server.db.models import UsersTable
from server.schemas.order import OrderCreate, OrderSchema, OrderUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


# def get_price_rules_total(order_items):
#     """Calculate the total number of grams."""
#     JOINT = 0.4
#
#     # Todo: add correct order line for 0.5 and 2.5
#     prices = {"0,5 gram": 0.5, "1 gram": 1, "2,5 gram": 2.5, "5 gram": 5, "joint": JOINT}
#     total = 0
#     for item in order_items:
#         if item["description"] in prices:
#             total = total + (prices[item["description"]] * item["quantity"])
#
#     return total


@router.get("/", response_model=List[OrderSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[OrderSchema]:
    orders, header_range = order_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    for order in orders:
        if (order.status == "complete" or order.status == "cancelled") and order.completed_by:
            order.completed_by_name = order.user.first_name
        if order.table_id:
            order.table_name = order.table.name
    response.headers["Content-Range"] = header_range
    return orders


# @router.get("/{id}", response_model=OrderWithDetails)
@router.get("/{id}")
def get_by_id(id: UUID) -> OrderSchema:
    pass


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(
    data: OrderCreate = Body(...), current_user: UsersTable = Depends(deps.get_current_active_superuser)
) -> None:
    logger.info("Saving order", data=data)
    order = order_crud.create(obj_in=data)
    return order


@router.put("/{order_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(
    *, order_id: UUID, item_in: OrderUpdate, current_user: UsersTable = Depends(deps.get_current_active_superuser)
) -> Any:
    order = order_crud.get(id=order_id)
    logger.info("Updating order", data=order)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    order = order_crud.update(
        db_obj=order,
        obj_in=item_in,
    )
    return order


@router.delete("/{order_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(order_id: UUID, current_user: UsersTable = Depends(deps.get_current_active_superuser)) -> None:
    return order_crud.delete(id=order_id)
