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
from server.crud.crud_kind import kind_crud
from server.crud.crud_kind_to_flavor import kind_to_flavor_crud
from server.schemas.kind_to_flavor import KindToFlavorCreate, KindToFlavorSchema, KindToFlavorUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[KindToFlavorSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[KindToFlavorSchema]:
    """List prices for a kind_to_flavor"""
    query_result, content_range = kind_to_flavor_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = content_range
    return query_result


@router.get("/{id}", response_model=KindToFlavorSchema)
def get_by_id(id: UUID) -> KindToFlavorSchema:
    kind_to_flavor = kind_to_flavor_crud.get(id)
    if not kind_to_flavor:
        raise_status(HTTPStatus.NOT_FOUND, f"KindToFlavor with id {id} not found")
    return kind_to_flavor


@router.post("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def create(data: KindToFlavorCreate = Body(...)) -> None:
    flavor = flavor_crud.get(data.flavor_id)
    kind = kind_crud.get(data.kind_id)

    if not flavor or not kind:
        raise_status(HTTPStatus.NOT_FOUND, "Flavor or kind not found")

    logger.info("Saving kind_to_flavor", data=data)
    return kind_to_flavor_crud.create(obj_in=data)


#
#
# @router.put("/{kind_to_flavor_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
# def update(*, kind_to_flavor_id: UUID, item_in: KindToFlavorUpdate) -> Any:
#     kind_to_flavor = kind_to_flavor_crud.get(id=kind_to_flavor_id)
#     logger.info("kind_to_flavor", data=kind_to_flavor)
#     if not kind_to_flavor:
#         raise HTTPException(status_code=404, detail="Shop not found")
#
#     kind_to_flavor = kind_to_flavor_crud.update(
#         db_obj=kind_to_flavor,
#         obj_in=item_in,
#     )
#     return kind_to_flavor
#
#
# @router.delete("/{kind_to_flavor_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
# def delete(kind_to_flavor_id: UUID) -> None:
#     return kind_to_flavor_crud.delete(id=kind_to_flavor_id)
