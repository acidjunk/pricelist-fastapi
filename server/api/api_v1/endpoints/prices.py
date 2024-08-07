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

from server.api.api_v1.router_fix import APIRouter
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_price import price_crud
from server.schemas.price import PriceCreate, PriceSchema, PriceUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[PriceSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[PriceSchema]:
    prices, header_range = price_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return prices


@router.get("/{id}", response_model=PriceSchema)
def get_by_id(id: UUID) -> PriceSchema:
    price = price_crud.get(id)
    if not price:
        raise_status(HTTPStatus.NOT_FOUND, f"Price with id {id} not found")
    return price


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: PriceCreate = Body(...)) -> None:
    logger.info("Saving price", data=data)
    try:
        price = price_crud.create(obj_in=data)
    except Exception as e:
        logger.error("Error saving price", error=e)
        raise HTTPException(status_code=400, detail=str(e))
    return price


@router.put("/{price_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, price_id: UUID, item_in: PriceUpdate) -> Any:
    price = price_crud.get(id=price_id)
    logger.info("Updating price", data=price)
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
