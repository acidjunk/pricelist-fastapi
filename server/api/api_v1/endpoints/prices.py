from http import HTTPStatus
from typing import List, Any
from uuid import UUID

from server.api.api_v1.router_fix import APIRouter
from fastapi.param_functions import Body, Depends
from fastapi import HTTPException
from starlette.responses import Response
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_price import price_crud
import structlog

from server.schemas.price import PriceCreate, PriceUpdate, PriceBase

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[PriceBase])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[PriceBase]:
    prices, header_range = price_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return prices


@router.get("/{id}", response_model=PriceBase)
def get_by_id(id: UUID) -> PriceBase:
    price = price_crud.get(id)
    if not price:
        raise_status(HTTPStatus.NOT_FOUND, f"Price with id {id} not found")
    return price


@router.post("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def create(data: PriceCreate = Body(...)) -> None:
    logger.info("Saving price", data=data)
    return price_crud.create(obj_in=data)


@router.put("/{price_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def update(*, price_id: UUID, item_in: PriceUpdate) -> Any:
    price = price_crud.get(id=price_id)
    logger.info("price", data=price)
    if not price:
        raise HTTPException(status_code=404, detail="Price not found")

    price = price_crud.update(
        db_obj=price,
        obj_in=item_in,
    )
    return price


@router.delete("/{price_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(price_id: UUID) -> None:
    return price_crud.delete(id=price_id)
