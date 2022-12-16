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
from server.api.helpers import invalidateShopCache
from server.crud.crud_category import category_crud
from server.crud.crud_kind import kind_crud
from server.crud.crud_product import product_crud
from server.crud.crud_shop import shop_crud
from server.crud.crud_shop_user import shop_user_crud
from server.crud.crud_user import user_crud
from server.db import db

# from server.db.models import ShopUser, UsersTable
from server.schemas.shop_user import ShopId, ShopUserCreate, ShopUserEmptyBase, ShopUserSchema, ShopUserUpdate, UserId
from server.schemas.user import UserShops

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/shop/{id}", response_model=List[UserId])
def get_users_by_shop(id: UUID) -> List[UserId]:
    return shop_user_crud.get_users_by_shop(shop_id=id)


@router.get("/user/{id}", response_model=List[ShopId])
def get_shops_by_user(id: UUID) -> List[ShopId]:
    return shop_user_crud.get_shops_by_user(user_id=id)


@router.post("/", status_code=HTTPStatus.CREATED)
def assign_shop_to_user(data: ShopUserCreate = Body(...)):
    if not user_crud.get(id=data.user_id):
        raise HTTPException(status_code=404, detail="User not found")
    if not shop_crud.get(id=data.shop_id):
        raise HTTPException(status_code=404, detail="Shop not found")

    shop_user_crud.create(obj_in=data)
    return {"message": "Shop assigned to user successfully!"}


@router.post("/assign-all/{user_id}", response_model=None, status_code=HTTPStatus.CREATED)
def assign_all_shops_to_user(user_id: UUID):
    user = user_crud.get(id=user_id)
    user_new = user_crud.get(id=user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    shops = shop_crud.get_multi(
        skip=0,
        limit=0,
        filter_parameters=[],
        sort_parameters=[],
    )
    shops_ids = []
    for shop in shops[0]:
        shops_ids.append(shop.id)
    # Maybe some help from Rene here ?
    user_crud.update(db_obj=user, obj_in=UserShops(shops=shops_ids))


@router.delete("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(shop_user: ShopUserEmptyBase):
    pass
