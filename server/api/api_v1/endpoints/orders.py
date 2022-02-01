from datetime import datetime
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
from server.api.utils import validate_uuid4
from server.crud.crud_order import order_crud
from server.crud.crud_shop import shop_crud
from server.crud.crud_shop_to_price import shop_to_price_crud
from server.db.models import UsersTable
from server.schemas.order import OrderCreate, OrderSchema, OrderUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


def get_price_rules_total(order_items):
    """Calculate the total number of grams."""
    JOINT = 0.4

    # Todo: add correct order line for 0.5 and 2.5
    prices = {"0,5 gram": 0.5, "1 gram": 1, "2,5 gram": 2.5, "5 gram": 5, "joint": JOINT}
    total = 0
    for item in order_items:
        if item.description in prices:
            total = total + (prices[item.description] * item.quantity)

    return total


def get_first_unavailable_product_name(order_items, shop_id):
    """Search for the first unavailable product and return it's name."""
    products = shop_to_price_crud.get_products_with_prices_by_shop_id(shop_id=shop_id)

    for item in order_items:
        found_product = False  # Start False
        for product in products:
            if item.kind_id == str(product.kind_id):
                if product.active:
                    if item.description == "0,5 gram" and (not product.use_half or not product.price.half):
                        logger.warning("Product is currently not available in 0.5 gram", kind_name=item.kind_name)
                    elif item.description == "1 gram" and (not product.use_one or not product.price.one):
                        logger.warning("Product is currently not available in 1 gram", kind_name=item.kind_name)
                    elif item.description == "2,5 gram" and (not product.use_two_five or not product.price.two_five):
                        logger.warning("Product is currently not available in 2.5 gram", kind_name=item.kind_name)
                    elif item.description == "5 gram" and (not product.use_five or not product.price.five):
                        logger.warning("Product is currently not available in 5 gram", kind_name=item.kind_name)
                    elif item.description == "1 joint" and (not product.use_joint or not product.price.joint):
                        logger.warning("Product is currently not available as joint", kind_name=item.kind_name)
                    else:
                        logger.info(
                            "Found product in order item and in available products",
                            kind_id=item.kind_id,
                            kind_name=item.kind_name,
                        )
                        found_product = True
                else:
                    logger.warning("Product is currently not available", kind_name=item.kind_name)
            if item.product_id == str(product.product_id):
                if product.active:
                    if not product.use_piece or not product.price.piece:
                        logger.warning("Product is currently not available as piece", product_name=item.product_name)
                    else:
                        logger.info(
                            "Found horeca product in order item and in available products",
                            product_id=item.product_id,
                            product_name=item.product_name,
                        )
                        found_product = True
                else:
                    logger.warning("Horeca product is currently not available", product_name=item.product_name)
        if not found_product:
            return item.kind_name if item.kind_name else item.product_name
    return None


@router.get("/", response_model=List[OrderSchema])
def get_multi(
    response: Response,
    common: dict = Depends(common_parameters),
    current_user: UsersTable = Depends(deps.get_current_active_user),
) -> List[OrderSchema]:
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


@router.get("/{id}")
def get_by_id(id: UUID) -> OrderSchema:
    order = order_crud.get(id)
    if not order:
        raise_status(HTTPStatus.NOT_FOUND, f"Order with id {id} not found")
    return order


@router.get("/check/{ids}")
def check(ids: str, current_user: UsersTable = Depends(deps.get_current_active_user)) -> List[OrderSchema]:
    id_list = ids.split(",")

    # Validate input
    for index, id in enumerate(id_list):
        if not validate_uuid4(id):
            raise_status(HTTPStatus.BAD_REQUEST, f"ID {index + 1} is not valid")

    if len(id_list) > 10:
        raise_status(HTTPStatus.BAD_REQUEST, "Max 10 orders")

    # Build response
    items = []
    for id in id_list:
        # item = load(Order, id, allow_404=True) #the old
        item = order_crud.get(id)
        if item:
            item.table_name = item.table.name
            items.append(item)

    for item in items:
        if item.shop_id != items[0].shop_id:
            raise_status(HTTPStatus.BAD_REQUEST, "All ID's should belong to one shop")

    return items


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: OrderCreate = Body(...)) -> None:
    logger.info("Saving order", data=data)

    if data.customer_order_id:
        del data.customer_order_id
    shop_id = data.shop_id
    if not shop_crud.get(str(shop_id)):
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {shop_id} not found")

    # 5 gram check
    total_cannabis = get_price_rules_total(data.order_info)
    logger.info("Checked order weight", weight=total_cannabis)
    if total_cannabis > 5:
        raise_status(HTTPStatus.BAD_REQUEST, "MAX_5_GRAMS_ALLOWED")

    # Availability check
    unavailable_product_name = get_first_unavailable_product_name(data.order_info, data.shop_id)
    if unavailable_product_name:
        raise_status(HTTPStatus.BAD_REQUEST, f"{unavailable_product_name}, OUT_OF_STOCK")

    data.customer_order_id = order_crud.get_newest_order_id(shop_id=shop_id)
    order = order_crud.create(obj_in=data)
    return order


@router.patch("/{order_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def patch(
    *, order_id: UUID, item_in: OrderUpdate, current_user: UsersTable = Depends(deps.get_current_active_user)
) -> Any:
    order = order_crud.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if (
        "complete" not in order.status
        and item_in.status
        and (item_in.status == "complete" or item_in.status == "cancelled")
        and not order.completed_at
    ):
        order.completed_at = datetime.utcnow()
        order.completed_by = current_user.id

    _ = order_crud.update(
        db_obj=order,
        obj_in=item_in,
    )
    return None


@router.put("/{order_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(
    *, order_id: UUID, item_in: OrderUpdate, current_user: UsersTable = Depends(deps.get_current_active_user)
) -> Any:
    order = order_crud.get(order_id)
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if item_in.status and (item_in.status == "complete" or item_in.status == "cancelled") and not order.completed_at:
        order.completed_at = datetime.utcnow()
        order.completed_by = current_user.id

    order = order_crud.update(
        db_obj=order,
        obj_in=item_in,
    )
    return order


@router.delete("/{order_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(order_id: UUID, current_user: UsersTable = Depends(deps.get_current_active_superuser)) -> None:
    return order_crud.delete(id=order_id)
