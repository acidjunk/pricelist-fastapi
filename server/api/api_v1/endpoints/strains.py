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
from server.crud.crud_strain import strain_crud
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


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: StrainCreate = Body(...)) -> None:
    logger.info("Saving strain", data=data)
    strain = strain_crud.create(obj_in=data)
    return strain


@router.put("/{strain_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, strain_id: UUID, item_in: StrainUpdate) -> Any:
    strain = strain_crud.get(id=strain_id)
    logger.info("Updating strain", data=strain)
    if not strain:
        raise HTTPException(status_code=404, detail="Strain not found")

    strain = strain_crud.update(
        db_obj=strain,
        obj_in=item_in,
    )
    return strain


@router.delete("/{strain_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(strain_id: UUID) -> None:
    return strain_crud.delete(id=strain_id)
