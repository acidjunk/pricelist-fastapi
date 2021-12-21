from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api import deps
from server.api.api_v1.router_fix import APIRouter
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_kind import kind_crud
from server.db.models import UsersTable
from server.schemas.kind import KindCreate, KindSchema, KindUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[KindSchema])
def get_multi(
    response: Response,
    common: dict = Depends(common_parameters),
    current_user: UsersTable = Depends(deps.get_current_active_superuser),
) -> List[KindSchema]:
    kinds, header_range = kind_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range
    return kinds


@router.get("/{id}", response_model=KindSchema)
def get_by_id(id: UUID) -> KindSchema:
    kind = kind_crud.get(id)
    if not kind:
        raise_status(HTTPStatus.NOT_FOUND, f"Kind with id {id} not found")
    return kind


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: KindCreate = Body(...), current_user: UsersTable = Depends(deps.get_current_active_superuser)) -> None:
    logger.info("Saving kind", data=data)
    kind = kind_crud.create(obj_in=data)
    return kind


@router.put("/{kind_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(
    *, kind_id: UUID, item_in: KindUpdate, current_user: UsersTable = Depends(deps.get_current_active_superuser)
) -> Any:
    kind = kind_crud.get(id=kind_id)
    logger.info("domain_event", data=kind)
    if not kind:
        raise HTTPException(status_code=404, detail="Kind not found")

    kind = kind_crud.update(
        db_obj=kind,
        obj_in=item_in,
    )
    return kind


@router.delete("/{kind_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(kind_id: UUID, current_user: UsersTable = Depends(deps.get_current_active_superuser)) -> None:
    return kind_crud.delete(id=kind_id)
