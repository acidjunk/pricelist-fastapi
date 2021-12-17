from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.api_v1.router_fix import APIRouter
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.apis.v1.helpers import load
from server.crud.crud_shop import shop_crud
from server.db.models import Category, Price, Shop, ShopToPrice
from server.schemas.shop import ShopCacheStatus, ShopCreate, ShopSchema, ShopUpdate, ShopWithPrices

router = APIRouter()
logger = structlog.get_logger(__name__)


@router.get("/", response_model=List[ShopSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[ShopSchema]:
    shops, header_range = shop_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return shops


@router.post("/", response_model=ShopSchema, status_code=HTTPStatus.CREATED)
def create(data: ShopCreate = Body(...)) -> ShopSchema:
    logger.info("Saving shop", data=data)
    shop = shop_crud.create(obj_in=data)
    return shop


@router.get("/cache-status/{id}", response_model=ShopCacheStatus)
def get_cache_status(id: UUID) -> ShopCacheStatus:
    """Show date of last change in data that could be visible in this shop"""
    shop = shop_crud.get(id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")
    return shop


@router.get("/{id}", response_model=ShopWithPrices)
def get_by_id(id: UUID):
    """List Shop"""
    item = load(Shop, id)
    price_relations = (
        ShopToPrice.query.filter_by(shop_id=item.id)
        .join(ShopToPrice.price)
        .join(ShopToPrice.category)
        .order_by(Category.name, Price.piece, Price.joint, Price.one, Price.five, Price.half, Price.two_five)
        .all()
    )
    item.prices = [
        {
            "id": pr.id,
            "internal_product_id": int(pr.price.internal_product_id),
            "active": pr.active,
            "new": pr.new,
            "category_id": pr.category_id,
            "category_name": pr.category.name,
            "category_name_en": pr.category.name_en,
            "category_icon": pr.category.icon,
            "category_color": pr.category.color,
            "category_order_number": pr.category.order_number,
            "category_image_1": pr.category.image_1,
            "category_image_2": pr.category.image_2,
            "main_category_id": pr.category.main_category.id if pr.category.main_category else "Unknown",
            "main_category_name": pr.category.main_category.name if pr.category.main_category else "Unknown",
            "main_category_name_en": pr.category.main_category.name_en if pr.category.main_category else "Unknown",
            "main_category_icon": pr.category.main_category.icon if pr.category.main_category else "Unknown",
            "main_category_order_number": pr.category.main_category.order_number if pr.category.main_category else 0,
            "kind_id": pr.kind_id,
            "kind_image": pr.kind.image_1 if pr.kind_id else None,
            "kind_name": pr.kind.name if pr.kind_id else None,
            "strains": [dict({"name": strain.strain.name}) for strain in pr.kind.kind_to_strains] if pr.kind_id else [],
            "kind_short_description_nl": pr.kind.short_description_nl if pr.kind_id else None,
            "kind_short_description_en": pr.kind.short_description_en if pr.kind_id else None,
            "kind_c": pr.kind.c if pr.kind_id else None,
            "kind_h": pr.kind.h if pr.kind_id else None,
            "kind_i": pr.kind.i if pr.kind_id else None,
            "kind_s": pr.kind.s if pr.kind_id else None,
            "product_id": pr.product_id,
            "product_image": pr.product.image_1 if pr.product_id else None,
            "product_name": pr.product.name if pr.product_id else None,
            "product_short_description_nl": pr.product.short_description_nl if pr.product_id else None,
            "product_short_description_en": pr.product.short_description_en if pr.product_id else None,
            "half": pr.price.half if pr.use_half else None,
            "one": pr.price.one if pr.use_one else None,
            "two_five": pr.price.two_five if pr.use_two_five else None,
            "five": pr.price.five if pr.use_five else None,
            "joint": pr.price.joint if pr.use_joint else None,
            "piece": pr.price.piece if pr.use_piece else None,
            "created_at": pr.created_at,
            "modified_at": pr.modified_at,
        }
        for pr in price_relations
    ]
    return item


@router.put("/{shop_id}", response_model=ShopSchema, status_code=HTTPStatus.CREATED)
def update(*, shop_id: UUID, item_in: ShopUpdate) -> None:
    shop = shop_crud.get(id=shop_id)
    logger.info("shop", data=shop)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    shop = shop_crud.update(
        db_obj=shop,
        obj_in=item_in,
    )
    return shop


@router.delete("/{shop_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(shop_id: UUID) -> None:
    return shop_crud.delete(id=shop_id)
