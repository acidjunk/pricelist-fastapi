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

from server.schemas.shop import ShopCreate, ShopUpdate, ShopBase

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ShopBase])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[ShopBase]:
    shops, header_range = shop_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return shops


@router.get("/{id}", response_model=ShopBase)
def get_by_id(id: UUID) -> ShopBase:
    shop = shop_crud.get(id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")
    return shop


@router.post("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def create(data: ShopCreate = Body(...)) -> None:
    logger.info("Saving shop", data=data)
    return shop_crud.create(obj_in=data)


@router.put("/{shop_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def update(*, shop_id: UUID, item_in: ShopUpdate) -> Any:
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
