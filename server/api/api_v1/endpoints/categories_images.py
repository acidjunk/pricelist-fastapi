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
from server.api.helpers import name_file, upload_file
from server.crud.crud_category import category_crud
from server.crud.crud_shop import shop_crud
from server.db.models import Category, Price, Shop, ShopToPrice
from server.schemas.category import CategoryUpdate

logger = structlog.get_logger(__name__)
router = APIRouter()

# file_upload = reqparse.RequestParser()


@router.get("/")
def get_multi(response: Response, common: dict = Depends(common_parameters)):
    """List all product category images"""
    categories, header_range = category_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return categories


@router.get("/{id}")
def get_by_id(id: UUID):
    category = category_crud.get(id)
    if not category:
        raise_status(HTTPStatus.NOT_FOUND, f"Category with id {id} not found")
    return category


@router.put("/{id}", status_code=HTTPStatus.CREATED)
def put(*, id: UUID, item_in: CategoryUpdate):
    item = category_crud.get(id=id)
    # todo: raise 404 o abort

    data = dict(item_in)

    category_update = False
    image_cols = ["image_1", "image_2"]
    for image_col in image_cols:
        if data.get(image_col) and type(data[image_col]) == dict:
            name = name_file(image_col, item.name, getattr(item, image_col))
            upload_file(data[image_col]["src"], name)  # todo: use mime-type in first part of
            category_update = True
            item_in.__setattr__(image_col, name)
        else:
            item_in.__setattr__(image_col, None)

    if category_update:
        item = category_crud.update(
            db_obj=item,
            obj_in=item_in,
        )

    return item


# @api.route("/delete/<id>")
# @api.doc("Image delete operations.")
# class CategoryImageDeleteResource(Resource):
#     @api.expect(delete_serializer)
#     @marshal_with(image_serializer)
#     def put(self, id):
#         image_cols = ["image_1", "image_2"]
#         item = load(Category, id)
#
#         image = api.payload["image"]
#         if image in image_cols:
#             setattr(item, image, "")
#             save(item)
#
#         return item, 201
