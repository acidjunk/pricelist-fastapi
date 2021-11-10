from server.crud.base import CRUDBase
from server.db.models import Category
from server.schemas.category import CategoryCreate, CategoryUpdate


class CRUDCategory(CRUDBase[Category, CategoryCreate, CategoryUpdate]):
    pass


category_crud = CRUDCategory(Category)
