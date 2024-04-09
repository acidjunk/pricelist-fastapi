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
from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

import structlog
from fastapi import HTTPException
from fastapi.param_functions import Body

from server.api.api_v1.router_fix import APIRouter
from server.api.helpers import get_shops_by_user_id, get_users_by_shop_id
from server.crud.crud_shop import shop_crud
from server.crud.crud_shop_user import shop_user_crud
from server.crud.crud_user import user_crud
from server.schemas.shop_user import ShopId, ShopUserCreate, ShopUserSchema, UserId

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/shop/{id}", response_model=List[UserId])
def get_users_by_shop(id: UUID) -> list[Optional[ShopUserSchema]]:
    return get_users_by_shop_id(shop_id=id)


@router.get("/user/{id}", response_model=List[ShopId])
def get_shops_by_user(id: UUID) -> list[Optional[ShopUserSchema]]:
    return get_shops_by_user_id(user_id=id)


@router.post("/", status_code=HTTPStatus.CREATED)
def assign_shop_to_user(data: ShopUserCreate = Body(...)):
    if not user_crud.get(id=data.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    if not shop_crud.get(id=data.shop_id):
        raise HTTPException(status_code=404, detail="Shop not found")

    shop_user_crud.create(obj_in=data)
    return {"message": "Shop assigned to user successfully!"}


@router.delete("/{relation_id}")
def delete(relation_id: UUID):
    shop_user = shop_user_crud.get(id=relation_id)
    if not shop_user:
        raise HTTPException(status_code=404, detail="Shop-User relation not found")

    shop_user_crud.delete(id=relation_id)
    return {"message": f"User removed from shop successfully!"}
