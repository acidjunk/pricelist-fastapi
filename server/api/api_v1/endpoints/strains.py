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
from typing import Any, List, Optional
from uuid import UUID

import structlog
from fastapi import HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.api_v1.router_fix import APIRouter
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_strain import strain_crud
from server.forms.new_product_form import validate_strain_name
from server.schemas.strain import StrainCreate, StrainSchema, StrainUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[StrainSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[StrainSchema]:
    strains, header_range = strain_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range
    return strains


@router.get("/{id}", response_model=StrainSchema)
def get_by_id(id: UUID) -> StrainSchema:
    strain = strain_crud.get(id)
    if not strain:
        raise_status(HTTPStatus.NOT_FOUND, f"Strain with id {id} not found")
    return strain


@router.get("/name/{name}", response_model=StrainSchema)
def get_by_name(name: str) -> StrainSchema:
    strain = strain_crud.get_by_name(name=name)

    if not strain:
        raise_status(HTTPStatus.NOT_FOUND, f"Strain with name {name} not found")
    return strain


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: StrainCreate = Body(...)) -> None:
    logger.info("Saving strain", data=data)
    try:
        validate_strain_name(strain_name=data.name, values={})
    except Exception:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail="Strain with this name already exists")

    strain = strain_crud.create(obj_in=data)
    return strain


@router.put("/{strain_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, strain_id: UUID, item_in: StrainUpdate) -> Any:
    strain = strain_crud.get(id=strain_id)
    logger.info("Updating strain", data=strain)
    if not strain:
        raise HTTPException(status_code=404, detail="Strain not found")

    try:
        validate_strain_name(strain_name=item_in.name, values={})
    except Exception:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail="Strain with this name already exists")

    strain = strain_crud.update(
        db_obj=strain,
        obj_in=item_in,
    )
    return strain


@router.delete("/{strain_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(strain_id: UUID) -> None:
    try:
        strain_crud.delete(id=strain_id)
    except Exception as e:
        raise HTTPException(HTTPStatus.BAD_REQUEST, detail=f"{e.__cause__}")
    return
