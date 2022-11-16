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
from server.api.helpers import invalidateShopCache
from server.crud.crud_kind import kind_crud
from server.crud.crud_kind_to_strain import kind_to_strain_crud
from server.crud.crud_strain import strain_crud
from server.schemas.kind_to_strain import KindToStrainCreate, KindToStrainSchema, KindToStrainUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[KindToStrainSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[KindToStrainSchema]:
    """List prices for a kind_to_strain"""
    query_result, content_range = kind_to_strain_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = content_range
    return query_result


@router.get("/{id}", response_model=KindToStrainSchema)
def get_by_id(id: UUID) -> KindToStrainSchema:
    kind_to_strain = kind_to_strain_crud.get(id)
    if not kind_to_strain:
        raise_status(HTTPStatus.NOT_FOUND, f"KindToStrain with id {id} not found")
    return kind_to_strain


@router.post("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def create(data: KindToStrainCreate = Body(...)) -> None:
    strain = strain_crud.get(data.strain_id)
    kind = kind_crud.get(data.kind_id)

    if not strain or not kind:
        raise_status(HTTPStatus.NOT_FOUND, "Strain or kind not found")

    logger.info("Saving kind_to_strain", data=data)

    result = kind_to_strain_crud.create(obj_in=data)

    # Todo fix for real
    invalidateShopCache("19149768-691c-40d8-a08e-fe900fd23bc0")

    return result


@router.put("/{kind_to_strain_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def update(*, kind_to_strain_id: UUID, item_in: KindToStrainUpdate) -> Any:
    kind_to_strain = kind_to_strain_crud.get(id=kind_to_strain_id)
    logger.info("Updating kind_to_strain", data=kind_to_strain)
    if not kind_to_strain:
        raise HTTPException(status_code=404, detail="Shop not found")

    kind_to_strain = kind_to_strain_crud.update(
        db_obj=kind_to_strain,
        obj_in=item_in,
    )

    # Todo fix for real
    invalidateShopCache("19149768-691c-40d8-a08e-fe900fd23bc0")

    return kind_to_strain


@router.delete("/{kind_to_strain_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(kind_to_strain_id: UUID) -> None:
    return kind_to_strain_crud.delete(id=kind_to_strain_id)
