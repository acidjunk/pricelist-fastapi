from http import HTTPStatus
from typing import List, Any
from uuid import UUID

from fastapi.routing import APIRouter
from fastapi.param_functions import Body, Depends
from fastapi import HTTPException
from starlette.responses import Response
from server.apis.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_strain import strain_crud
import structlog

from server.schemas.strain import StrainCreate, StrainSchema, StrainUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/")
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


@router.post("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def create(data: StrainCreate = Body(...)) -> None:
    logger.info("Saving strain", data=data)
    return strain_crud.create(obj_in=data)


@router.put("/{strain_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def update(*, strain_id: UUID, item_in: StrainUpdate) -> Any:
    strain = strain_crud.get(id=strain_id)
    logger.info("domain_event", data=strain)
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
