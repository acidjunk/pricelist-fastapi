from http import HTTPStatus
from typing import List, Any
from uuid import UUID

from fastapi.routing import APIRouter
from fastapi.param_functions import Body, Depends
from fastapi import HTTPException
from starlette.responses import Response
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_shop import shop_crud
import structlog

from server.crud.crud_shop_to_price import shop_to_price_crud
from server.schemas.shop_to_price import ShopToPriceBase, ShopToPriceCreate, ShopToPriceUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ShopToPriceBase])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[ShopToPriceBase]:
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


# @router.get("/{id}", response_model=ShopToPriceBase)
# def get_by_id(id: UUID) -> ShopToPriceBase:
#     shop = shop_crud.get(id)
#     if not shop:
#         raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")
#     return shop
#
#
# @router.post("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
# def create(data: ShopToPriceCreate = Body(...)) -> None:
#     logger.info("Saving shop", data=data)
#     return shop_crud.create(obj_in=data)
#
#
# @router.put("/{shop_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
# def update(*, shop_id: UUID, item_in: ShopToPriceUpdate) -> Any:
#     shop = shop_crud.get(id=shop_id)
#     logger.info("shop", data=shop)
#     if not shop:
#         raise HTTPException(status_code=404, detail="Shop not found")
#
#     shop = shop_crud.update(
#         db_obj=shop,
#         obj_in=item_in,
#     )
#     return shop
#
#
# @router.delete("/{shop_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
# def delete(shop_id: UUID) -> None:
#     return shop_crud.delete(id=shop_id)
