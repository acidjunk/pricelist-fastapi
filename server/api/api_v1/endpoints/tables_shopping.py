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
from http import HTTPStatus
from uuid import UUID

import structlog
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api import deps
from server.api.api_v1.router_fix import APIRouter
from server.api.error_handling import raise_status
from server.api.utils import is_user_allowed_in_shop, raise_on_user_is_allowed
from server.crud.crud_table import table_crud
from server.db.models import UsersTable
from server.schemas.table import TableCreate, TableSchema

logger = structlog.get_logger(__name__)

router = APIRouter()


# Table name is used as an e-mail address for the order
@router.get("/name/{table_name}", response_model=TableSchema)
def get_table_by_table_name(
    table_name: str, current_user: UsersTable = Depends(deps.get_current_active_table_moderator)
) -> UUID:
    table = table_crud.get_by_name(name=table_name)

    if not table:
        raise_status(HTTPStatus.NOT_FOUND, f"Table with name {table_name} not found")

    raise_on_user_is_allowed(is_user_allowed_in_shop(user=current_user, shop_id=table.shop_id))
    return table


@router.post("/", response_model=TableSchema)
def get_or_create_table_by_name(
    response: Response,
    data: TableCreate = Body(...),
    current_user: UsersTable = Depends(deps.get_current_active_table_moderator),
) -> None:
    logger.info("Saving table", data=data)
    raise_on_user_is_allowed(is_user_allowed_in_shop(user=current_user, shop_id=data.shop_id))

    table = table_crud.get_by_name(name=data.name)
    if table:
        response.status_code = HTTPStatus.OK
        return table

    response.status_code = HTTPStatus.CREATED
    table = table_crud.create(obj_in=data)
    return table
