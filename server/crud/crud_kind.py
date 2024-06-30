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
from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import Kind
from server.schemas.kind import KindCreate, KindUpdate


class CRUDKind(CRUDBase[Kind, KindCreate, KindUpdate]):
    def get_all_by_shop_group_id(self, *, shop_group_id: str) -> Optional[Kind]:
        return Kind.query.filter(Kind.shop_group_id == shop_group_id).all()


kind_crud = CRUDKind(Kind)
