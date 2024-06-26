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
from server.crud.crud_flavor import flavor_crud
from server.schemas.flavor import FlavorCreate, FlavorSchema, FlavorUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[FlavorSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[FlavorSchema]:
    flavors, header_range = flavor_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range
    return flavors


@router.get("/{id}", response_model=FlavorSchema)
def get_by_id(id: UUID) -> FlavorSchema:
    flavor = flavor_crud.get(id)
    if not flavor:
        raise_status(HTTPStatus.NOT_FOUND, f"Flavor with id {id} not found")
    return flavor


# Todo: unit tests
@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: FlavorCreate = Body(...)) -> None:
    logger.info("Saving flavor", data=data)

    if flavor_crud.get_flavor_by_name(name=data.name):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Flavor with this name already exists")

    flavor = flavor_crud.create(obj_in=data)
    return flavor


@router.put("/{flavor_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, flavor_id: UUID, item_in: FlavorUpdate) -> Any:
    flavor = flavor_crud.get(id=flavor_id)
    logger.info("Updating flavor", data=flavor)
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found")

    if flavor_crud.get_flavor_by_name(name=item_in.name):
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail="Flavor with this name already exists")

    flavor = flavor_crud.update(
        db_obj=flavor,
        obj_in=item_in,
    )
    return flavor


@router.delete("/{flavor_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(flavor_id: UUID) -> None:
    return flavor_crud.delete(id=flavor_id)
