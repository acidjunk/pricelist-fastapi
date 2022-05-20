from datetime import datetime

import time
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
from server.api.helpers import invalidateShopCache
from server.apis.v1.helpers import load, save
from server.crud.crud_category import category_crud
from server.crud.crud_kind import kind_crud
from server.crud.crud_price import price_crud
from server.crud.crud_product import product_crud
from server.crud.crud_shop import shop_crud
from server.crud.crud_shop_to_price import shop_to_price_crud
from server.db.models import UsersTable, Shop
from server.schemas.shop import ShopUpdate
from server.schemas.shop_to_price import (
    ShopToPriceAvailability,
    ShopToPriceCreate,
    ShopToPriceSchema,
    ShopToPriceUpdate,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ShopToPriceSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[ShopToPriceSchema]:
    """List prices for a shop"""
    query_result, content_range = shop_to_price_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = content_range

    for result in query_result:
        result.half = result.price.half if result.price.half and result.use_half else None
        result.one = result.price.one if result.price.one and result.use_one else None
        result.two_five = result.price.two_five if result.price.two_five and result.use_two_five else None
        result.five = result.price.five if result.price.five and result.use_five else None
        result.joint = result.price.joint if result.price.joint and result.use_joint else None
        result.piece = result.price.piece if result.price.piece and result.use_piece else None

    return query_result


@router.get("/{id}", response_model=ShopToPriceSchema)
def get_by_id(id: UUID) -> ShopToPriceSchema:
    item = shop_to_price_crud.get(id)
    if not item:
        raise_status(HTTPStatus.NOT_FOUND, f"Relation shop_to_price with id {id} not found")
    price = price_crud.get(item.price_id)
    item.half = price.half if price.half else None
    item.one = price.one if price.one else None
    item.two_five = price.two_five if price.two_five else None
    item.five = price.five if price.five else None
    item.joint = price.joint if price.joint else None
    item.piece = price.piece if price.piece else None
    return item


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(
    data: ShopToPriceCreate = Body(...), current_user: UsersTable = Depends(deps.get_current_active_superuser)
) -> None:
    logger.info("Saving shop to price relation", data=data)
    price = price_crud.get(data.price_id)
    shop = shop_crud.get(data.shop_id)
    kind = kind_crud.get(data.kind_id) or None
    product = product_crud.get(data.product_id) or None
    category = category_crud.get(data.category_id) or None

    if not price or not shop:
        raise_status(HTTPStatus.NOT_FOUND, "Price or Shop not found")

    if (product and kind) or not product and not kind:
        raise_status(HTTPStatus.BAD_REQUEST, "Either one Cannabis or one Horeca product has to be provided")

    if kind:
        check_query = shop_to_price_crud.check_relation_by_kind(shop_id=shop.id, price_id=price.id, kind_id=kind.id)
        if len(check_query) > 0:
            raise_status(HTTPStatus.CONFLICT, "Relation already exists")

    if product:
        check_query = shop_to_price_crud.check_relation_by_product(
            shop_id=shop.id, price_id=price.id, product_id=product.id
        )
        if len(check_query) > 0:
            raise_status(HTTPStatus.CONFLICT, "Relation already exists")

    shop_to_price = ShopToPriceCreate(
        active=data.active if data.active else False,
        new=data.new if data.new else False,
        kind_id=kind.id if kind else None,
        product_id=product.id if product else None,
        category_id=category.id if category else None,
        shop_id=shop.id if shop else None,
        price_id=price.id if price else None,
        use_half=data.use_half if data.use_half else False,
        use_one=data.use_one if data.use_one else False,
        use_two_five=data.use_two_five if data.use_two_five else False,
        use_five=data.use_five if data.use_five else False,
        use_joint=data.use_joint if data.use_joint else False,
        use_piece=data.use_piece if data.use_piece else False,
    )

    invalidateShopCache(shop_to_price.shop_id)
    return shop_to_price_crud.create(obj_in=shop_to_price)


@router.put("/{shop_to_price_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def update(
    *,
    shop_to_price_id: UUID,
    item_in: ShopToPriceUpdate,
    # current_user: UsersTable = Depends(deps.get_current_active_superuser),
) -> Any:
    shop_to_price = shop_to_price_crud.get(id=shop_to_price_id)

    logger.info("Updating shop_to_price", data=shop_to_price)
    if not shop_to_price:
        raise HTTPException(status_code=404, detail="Shop to price not found")

    price = price_crud.get(item_in.price_id)
    shop = shop_crud.get(item_in.shop_id)
    kind = kind_crud.get(item_in.kind_id) or None
    product = product_crud.get(item_in.product_id) or None

    if not price or not shop:
        raise_status(HTTPStatus.NOT_FOUND, "Price or Shop not found")

    if (product and kind) or not product and not kind:
        raise_status(HTTPStatus.BAD_REQUEST, "One Cannabis or one Horeca product has to be provided")

    # invalidateShopCache(item_in.shop_id)
    # item = shop_crud.get(item_in.shop_id)
    item = load(Shop, item_in.shop_id)
    item.modified_at = datetime.utcnow()
    save(item)

    # item_in_2 = ShopUpdate(
    #     name=item.name,
    #     description=item.description,
    #     modified_at=datetime.utcnow(),
    #     last_pending_order=item.last_pending_order,
    #     last_completed_order=item.last_completed_order
    # )
    # # sendMessageToWebSocketServer(payload)
    # Ok we survived all that: let's save it:
    # cola = shop_crud.update(db_obj=item, obj_in=item_in_2)

    shop_to_price_crud.update(
        db_obj=shop_to_price,
        obj_in=item_in,
    )

    return "seedb"



@router.put("/availability/{shop_to_price_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def update(
    *,
    shop_to_price_id: UUID,
    item_in: ShopToPriceAvailability,
    current_user: UsersTable = Depends(deps.get_current_active_superuser),
) -> Any:
    shop_to_price = shop_to_price_crud.get(id=shop_to_price_id)
    invalidateShopCache(shop_to_price.shop_id)
    return shop_to_price_crud.update(
        db_obj=shop_to_price,
        obj_in=item_in,
    )


@router.delete("/{shop_to_price_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(shop_to_price_id: UUID, current_user: UsersTable = Depends(deps.get_current_active_superuser)) -> None:
    shop_to_price = shop_to_price_crud.get(id=shop_to_price_id)
    if not shop_to_price:
        raise HTTPException(status_code=404, detail="Shop to price not found")
    invalidateShopCache(shop_to_price.shop_id)
    return shop_to_price_crud.delete(id=shop_to_price_id)
