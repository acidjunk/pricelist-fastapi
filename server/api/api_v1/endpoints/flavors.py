from http import HTTPStatus
from typing import List, Any
from uuid import UUID

from fastapi.routing import APIRouter
from fastapi.param_functions import Body, Depends
from fastapi import HTTPException
from starlette.responses import Response
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_flavor import flavor_crud
import structlog

from server.schemas.flavor import FlavorCreate, FlavorSchema, FlavorUpdate, FlavorBase

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[FlavorBase])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[FlavorBase]:
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


@router.post("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def create(data: FlavorCreate = Body(...)) -> None:
    logger.info("Saving flavor", data=data)
    return flavor_crud.create(obj_in=data)


@router.put("/{flavor_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def update(*, flavor_id: UUID, item_in: FlavorUpdate) -> Any:
    flavor = flavor_crud.get(id=flavor_id)
    logger.info("domain_event", data=flavor)
    if not flavor:
        raise HTTPException(status_code=404, detail="Flavor not found")

    flavor = flavor_crud.update(
        db_obj=flavor,
        obj_in=item_in,
    )
    return flavor


@router.delete("/{flavor_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(flavor_id: UUID) -> None:
    return flavor_crud.delete(id=flavor_id)
