from typing import List, Optional
from uuid import UUID

from server.crud.base import CRUDBase
from server.db.models import ShopsUsersTable
from server.schemas.shop_user import ShopUserCreate, ShopUserEmptyBase, ShopUserSchema, ShopUserUpdate


class CRUDShopUser(CRUDBase[ShopsUsersTable, ShopUserCreate, ShopUserUpdate]):
    def get_shops_by_user(self, *, user_id: UUID) -> List[Optional[ShopUserSchema]]:
        query = ShopsUsersTable.query.filter_by(user_id=user_id).all()
        return query

    def get_users_by_shop(self, *, shop_id: UUID) -> List[Optional[ShopUserSchema]]:
        query = ShopsUsersTable.query.filter_by(shop_id=shop_id).all()
        return query


shop_user_crud = CRUDShopUser(ShopsUsersTable)
