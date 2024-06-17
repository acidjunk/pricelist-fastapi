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
from server.crud.crud_shop import shop_crud
from server.crud.crud_shop_group import shop_group_crud
from server.forms.new_product_form import validate_shop_group_name
from server.schemas.shop_group import ShopGroupCreate, ShopGroupSchema, ShopGroupUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ShopGroupSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[ShopGroupSchema]:
    shop_groups, header_range = shop_group_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range
    return shop_groups


@router.get("/{id}", response_model=ShopGroupSchema)
def get_by_id(id: UUID) -> ShopGroupSchema:
    shop_group = shop_group_crud.get(id)
    if not shop_group:
        raise_status(HTTPStatus.NOT_FOUND, f"shop_group with id {id} not found")
    return shop_group


@router.get("/name/{name}", response_model=ShopGroupSchema)
def get_by_name(name: str) -> ShopGroupSchema:
    shop_group = shop_group_crud.get_by_name(name=name)

    if not shop_group:
        raise_status(HTTPStatus.NOT_FOUND, f"shop_group with name {name} not found")
    return shop_group


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: ShopGroupCreate = Body(...)) -> None:
    logger.info("Saving shop_group", data=data)
    try:
        validate_shop_group_name(shop_group_name=data.name, values={})
    except Exception:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail="shop_group with this name already exists")

    shop_group = shop_group_crud.create_shop_group(obj_in=data)
    return shop_group


@router.put("/{shop_group_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, shop_group_id: UUID, item_in: ShopGroupUpdate) -> Any:
    shop_group = shop_group_crud.get(id=shop_group_id)
    logger.info("Updating shop_group", data=shop_group)
    if not shop_group:
        raise HTTPException(status_code=404, detail="shop_group not found")

    for shop_id in item_in.shop_ids:
        if not shop_crud.get(str(shop_id)):
            raise HTTPException(HTTPStatus.BAD_REQUEST, detail=f"Shop with id {shop_id} not found")

    shop_group = shop_group_crud.update(
        db_obj=shop_group,
        obj_in=item_in,
    )
    return shop_group


@router.delete("/{shop_group_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(shop_group_id: UUID) -> None:
    try:
        shop_group_crud.delete(id=shop_group_id)
    except Exception as e:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail=f"{e.__cause__}")
    return
