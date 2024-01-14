from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import Table
from server.schemas.table import TableCreate, TableUpdate


class CRUDTable(CRUDBase[Table, TableCreate, TableUpdate]):
    def get_by_name(self, *, name: str) -> Optional[Table]:
        return Table.query.filter(Table.name == name).first()


table_crud = CRUDTable(Table)
