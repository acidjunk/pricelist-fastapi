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
from server.crud.crud_product import product_crud
from server.db.models import UsersTable
from server.schemas.product import ProductCreate, ProductSchema, ProductUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[ProductSchema])
def get_multi(
    response: Response,
    common: dict = Depends(common_parameters),
    current_user: UsersTable = Depends(deps.get_current_active_superuser),
) -> List[ProductSchema]:
    products, header_range = product_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range
    return products


@router.get("/{id}", response_model=ProductSchema)
def get_by_id(id: UUID) -> ProductSchema:
    product = product_crud.get(id)
    if not product:
        raise_status(HTTPStatus.NOT_FOUND, f"Product with id {id} not found")
    return product


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(
    data: ProductCreate = Body(...), current_user: UsersTable = Depends(deps.get_current_active_superuser)
) -> None:
    logger.info("Saving product", data=data)
    product = product_crud.create(obj_in=data)
    return product


@router.put("/{product_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(
    *, product_id: UUID, item_in: ProductUpdate, current_user: UsersTable = Depends(deps.get_current_active_superuser)
) -> Any:
    product = product_crud.get(id=product_id)
    logger.info("Updating product", data=product)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")

    product = product_crud.update(
        db_obj=product,
        obj_in=item_in,
    )
    return product


@router.delete("/{product_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(product_id: UUID, current_user: UsersTable = Depends(deps.get_current_active_superuser)) -> None:
    product_crud.delete(id=product_id)
    return None
