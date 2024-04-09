# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
from datetime import datetime
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
from server.crud.crud_kind import kind_crud
from server.crud.crud_shop import shop_crud
from server.db.models import Category, Price, Shop, ShopToPrice
from server.schemas.kind import KindImageDelete, KindUpdate

logger = structlog.get_logger(__name__)
router = APIRouter()

# file_upload = reqparse.RequestParser()


@router.get("/")
def get_multi(response: Response, common: dict = Depends(common_parameters)):
    """List all product kind images"""
    kinds, header_range = kind_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return kinds


@router.get("/{id}")
def get_by_id(id: UUID):
    kind = kind_crud.get(id)
    if not kind:
        raise_status(HTTPStatus.NOT_FOUND, f"Kind with id {id} not found")
    return kind


@router.put("/{id}", status_code=HTTPStatus.CREATED)
def put(*, id: UUID, item_in: KindUpdate):
    item = kind_crud.get(id)
    if not item:
        raise_status(HTTPStatus.NOT_FOUND, f"Kind with id {id} not found")

    data = dict(item_in)
    kind_update = False
    image_cols = ["image_1", "image_2", "image_3", "image_4", "image_5", "image_6"]
    for image_col in image_cols:
        if data.get(image_col) and type(data[image_col]) == dict:
            name = name_file(image_col, item.name, getattr(item, image_col))
            upload_file(data[image_col]["src"], name) if item.name != "Test Kind" else None
            kind_update = True
            item_in.__setattr__(image_col, name)

    if kind_update:
        item_in.__setattr__(
            "complete", True if data.get("image_1") and item.description_nl and item.description_en else False
        )
        item_in.__setattr__("modified_at", datetime.utcnow())

        item = kind_crud.update(
            db_obj=item,
            obj_in=item_in,
        )

    return item


@router.put("/delete/{id}", status_code=HTTPStatus.CREATED)
def delete_image(*, id: UUID, col: KindImageDelete):
    item = kind_crud.get(id)

    if not item:
        raise_status(HTTPStatus.NOT_FOUND, f"Kind with id {id} not found")

    if not getattr(item, col.image):
        raise_status(HTTPStatus.NOT_FOUND, f"Kind with id {id} has no {col.image}")

    item_in = KindUpdate(**item.__dict__.copy())

    setattr(item_in, col.image, None)
    setattr(item_in, "modified_at", datetime.utcnow())

    item = kind_crud.update(
        db_obj=item,
        obj_in=item_in,
    )

    return item
