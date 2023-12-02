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
from server.crud.crud_main_category import main_category_crud
from server.schemas.main_category import (
    MainCategoryCreate,
    MainCategorySchema,
    MainCategoryUpdate,
    MainCategoryWithNames,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[MainCategoryWithNames])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[MainCategorySchema]:
    main_categories, header_range = main_category_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    for main_category in main_categories:
        main_category.shop_name = main_category.shop.name
        main_category.main_category_and_shop = f"{main_category.shop.name} - {main_category.name}"
    response.headers["Content-Range"] = header_range
    return main_categories


@router.get("/{id}", response_model=MainCategorySchema)
def get_by_id(id: UUID) -> MainCategorySchema:
    main_category = main_category_crud.get(id)
    if not main_category:
        raise_status(HTTPStatus.NOT_FOUND, f"MainCategory with id {id} not found")
    return main_category


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: MainCategoryCreate = Body(...)) -> None:
    logger.info("Saving main_category", data=data)
    return main_category_crud.create(obj_in=data)


@router.put("/{main_category_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(*, main_category_id: UUID, item_in: MainCategoryUpdate) -> Any:
    main_category = main_category_crud.get(id=main_category_id)
    logger.info("Updating main_category", data=main_category)
    if not main_category:
        raise HTTPException(status_code=404, detail="MainCategory not found")

    main_category = main_category_crud.update(
        db_obj=main_category,
        obj_in=item_in,
    )
    return main_category


@router.delete("/{main_category_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(main_category_id: UUID) -> None:
    return main_category_crud.delete(id=main_category_id)
