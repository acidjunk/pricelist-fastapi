from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import ShopsUsersTable
from server.schemas.shop_user import ShopUserCreate, ShopUserUpdate


class CRUDShopUser(CRUDBase[ShopsUsersTable, ShopUserCreate, ShopUserUpdate]):
    def get_all_by_user_id(self, *, user_id: str) -> Optional[ShopsUsersTable]:
        return ShopsUsersTable.query.filter(ShopsUsersTable.user_id == user_id).all()


shop_user_crud = CRUDShopUser(ShopsUsersTable)
