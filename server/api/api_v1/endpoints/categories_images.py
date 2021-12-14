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
from server.apis.v1.helpers import load, name_file
from server.crud import category_crud
from server.crud.crud_shop import shop_crud
from server.db.models import Category, Price, Shop, ShopToPrice
from server.schemas.category import CategoryUpdate

logger = structlog.get_logger(__name__)
router = APIRouter()

# file_upload = reqparse.RequestParser()

# @router.get("/")
# def get_multi(response: Response, common: dict = Depends(common_parameters)):
#     """List all product category images"""
#     args = parser.parse_args()
#     range = get_range_from_args(args)
#     sort = get_sort_from_args(args)
#     filter = get_filter_from_args(args)
#
#     query_result, content_range = query_with_filters(
#         Category,
#         Category.query,
#         range,
#         sort,
#         filter,
#         quick_search_columns=["name", "image_1", "image_2"],
#     )
#
#     return query_result, 200, {"Content-Range": content_range}


# @api.route("/<id>")
# def get(self, id):
#     """List Image"""
#     item = load(Category, id)
#     return item, 200


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
            # upload_file(data[image_col]["src"], name)  # todo: use mime-type in first part of
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
