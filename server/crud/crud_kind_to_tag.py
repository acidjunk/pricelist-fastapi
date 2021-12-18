from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import KindToTag
from server.schemas.kind_to_tag import KindToTagCreate, KindToTagUpdate


class CRUDKindToTag(CRUDBase[KindToTag, KindToTagCreate, KindToTagUpdate]):
    def get_relation(self, *, kind, tag) -> Optional[KindToTag]:
        return KindToTag.query.filter_by(kind_id=kind.id).filter_by(tag_id=tag.id).all()


kind_to_tag_crud = CRUDKindToTag(KindToTag)
