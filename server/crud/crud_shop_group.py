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

from server.api.models import transform_json_without_clean
from server.crud.base import CRUDBase
from server.db.models import ShopGroup
from server.schemas.shop_group import ShopGroupCreate, ShopGroupUpdate


class CRUDShopGroup(CRUDBase[ShopGroup, ShopGroupCreate, ShopGroupUpdate]):
    def get_by_name(self, *, name: str) -> Optional[ShopGroup]:
        return ShopGroup.query.filter(ShopGroup.name == name).first()

    def create(self, *, obj_in: ShopGroupCreate) -> ShopGroupCreate:
        obj_in_data = transform_json_without_clean(obj_in.dict())
        db_obj = self.model(**obj_in_data)
        ShopGroup.query.session.add(db_obj)
        ShopGroup.query.session.commit()
        ShopGroup.query.session.refresh(db_obj)
        return obj_in


shop_group_crud = CRUDShopGroup(ShopGroup)
