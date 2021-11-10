from http import HTTPStatus
from typing import List, Any
from uuid import UUID

from fastapi.routing import APIRouter
from fastapi.param_functions import Body, Depends
from fastapi import HTTPException
from starlette.responses import Response
from server.api.error_handling import raise_status

import structlog
from server.apis.v1.helpers import (
    load, name_file,
)
from server.api.deps import common_parameters
from server.crud import category_crud
from server.crud.crud_shop import shop_crud
from server.db.models import Category, Price, Shop, ShopToPrice

import structlog

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


@router.put("/{id}")
def put(*, id: UUID, item_in: CategoryUpdate):
    # args = file_upload.parse_args()
    # logger.warning("Ignoring files via args! (using JSON body)", args=args)
    item = category_crud.get(id=id)
    # todo: raise 404 o abort

    data = dict(item_in)

    category_update = [None, None]
    image_cols = ["image_1", "image_2"]
    for i in range(len(image_cols)):
        if data.get(image_cols[i]) and type(data[image_cols[i]]) == dict:
            name = name_file(image_cols[i], item.name, getattr(item, image_cols[i]))
            # upload_file(data[image_col]["src"], name)  # todo: use mime-type in first part of
            category_update[i] = name
            # item_in.__setattr__(image_cols[i], name)

    # if category_update:
    #     category_update["shop_id"] = item.shop_id
    #     item = update(item, category_update)

    for i in range(len(image_cols)):
        item_in.__setattr__(image_cols[i], category_update[i])

    if category_update:
        # category_update["shop_id"] = item.shop_id
        item = category_crud.update(
            db_obj=item,
            obj_in=item_in,
        )

    return item, 201


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
