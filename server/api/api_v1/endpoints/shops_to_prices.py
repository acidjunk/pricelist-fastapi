# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
from server.api.utils import is_user_allowed_in_shop, raise_on_user_is_allowed
from server.crud.crud_category import category_crud
from server.crud.crud_kind import kind_crud
from server.crud.crud_price import price_crud
from server.crud.crud_product import product_crud
from server.crud.crud_shop import shop_crud
from server.crud.crud_shop_to_price import shop_to_price_crud
from server.db import db
from server.db.models import ShopToPrice, UsersTable
from server.schemas.shop_to_price import (
    ShopToPriceAvailability,
    ShopToPriceCreate,
    ShopToPriceSchema,
    ShopToPriceSwap,
    ShopToPriceUpdate,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


def fix_sort(category_id):
    prices = (
        ShopToPrice.query.filter_by(category_id=category_id)
        .filter(ShopToPrice.product_id.isnot(None))
        .order_by(ShopToPrice.order_number)
        .all()
    )
    for count, price in enumerate(prices):
        shop_to_price_crud.update(db_obj=price, obj_in=ShopToPriceSwap(order_number=count), commit=False)
    db.session.commit()


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

    result = shop_to_price_crud.create(obj_in=shop_to_price)
    invalidateShopCache(shop_to_price.shop_id)
    return result


@router.put("/{shop_to_price_id}", response_model=ShopToPriceSchema, status_code=HTTPStatus.CREATED)
def update(
    *,
    shop_to_price_id: UUID,
    item_in: ShopToPriceUpdate,
    current_user: UsersTable = Depends(deps.get_current_active_superuser),
) -> ShopToPriceSchema:
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

    updated = shop_to_price_crud.update(db_obj=shop_to_price, obj_in=item_in, commit=False)
    invalidateShopCache(item_in.shop_id)
    return updated


@router.put("/availability/{shop_to_price_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def update(
    *,
    shop_to_price_id: UUID,
    item_in: ShopToPriceAvailability,
    current_user: UsersTable = Depends(deps.get_current_active_superuser),
) -> Any:
    shop_to_price = shop_to_price_crud.get(id=shop_to_price_id)

    result = shop_to_price_crud.update(
        db_obj=shop_to_price,
        obj_in=item_in,
    )
    invalidateShopCache(shop_to_price.shop_id)
    return result


@router.delete("/{shop_to_price_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(shop_to_price_id: UUID, current_user: UsersTable = Depends(deps.get_current_active_superuser)) -> None:
    shop_to_price = shop_to_price_crud.get(id=shop_to_price_id)
    if not shop_to_price:
        raise HTTPException(status_code=404, detail="Shop to price not found")

    result = shop_to_price_crud.delete(id=shop_to_price_id)
    invalidateShopCache(shop_to_price.shop_id)
    fix_sort(shop_to_price.category_id)
    return result


@router.patch("/swap/{shop_to_price_id}", status_code=HTTPStatus.CREATED)
def swap_order_numbers(
    shop_to_price_id: UUID, move_up: bool, current_user: UsersTable = Depends(deps.get_current_active_employee)
):
    shop_to_price = shop_to_price_crud.get(id=shop_to_price_id)

    raise_on_user_is_allowed(is_user_allowed_in_shop(user=current_user, shop_id=shop_to_price.shop_id))

    if not shop_to_price:
        raise HTTPException(status_code=404, detail="Shop to price not found")

    last_shop_to_price = (
        ShopToPrice.query.filter_by(category_id=shop_to_price.category_id)
        .order_by(ShopToPrice.order_number.desc())
        .first()
    )

    old_order_number = shop_to_price.order_number
    new_order_number = None

    if move_up:
        if old_order_number == 0:
            raise HTTPException(status_code=400, detail="Cannot move up further - Minimum order number achieved.")
        new_order_number = old_order_number - 1
    else:
        if old_order_number == last_shop_to_price.order_number:
            raise HTTPException(status_code=400, detail="Cannot move down further - Maximum order number achieved.")
        new_order_number = old_order_number + 1

    shop_to_price_to_swap = (
        ShopToPrice.query.filter_by(category_id=shop_to_price.category_id)
        .filter_by(order_number=new_order_number)
        .first()
    )

    shop_to_price_crud.update(db_obj=shop_to_price, obj_in=ShopToPriceSwap(order_number=new_order_number), commit=False)

    shop_to_price_crud.update(
        db_obj=shop_to_price_to_swap,
        obj_in=ShopToPriceSwap(order_number=old_order_number),
    )

    return f"shop_to_price with id {shop_to_price_id} moved to {new_order_number}"
