from server.crud.base import CRUDBase
from server.db.models import Tag
from server.schemas.flavor import TagCreate, TagUpdate


class CRUDTag(CRUDBase[Tag, TagCreate, TagUpdate]):
    pass


flavor_crud = CRUDTag(Tag)
