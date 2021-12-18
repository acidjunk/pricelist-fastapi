from server.crud.base import CRUDBase
from server.db.models import Tag
from server.schemas.tag import TagCreate, TagUpdate


class CRUDTag(CRUDBase[Tag, TagCreate, TagUpdate]):
    pass


tag_crud = CRUDTag(Tag)
