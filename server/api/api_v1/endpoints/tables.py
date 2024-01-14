from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from fastapi import HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api import deps
from server.api.api_v1.router_fix import APIRouter
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.api.utils import is_user_allowed_in_shop
from server.crud.crud_shop_user import shop_user_crud
from server.crud.crud_table import table_crud
from server.db.models import UsersTable
from server.schemas.table import TableCreate, TableSchema, TableUpdate

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[TableSchema])
def get_multi(
    response: Response,
    common: dict = Depends(common_parameters),
    current_user: UsersTable = Depends(deps.get_current_active_table_moderator),
) -> List[TableSchema]:
    tables, header_range = table_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range
    if any(role.name == "admin" for role in current_user.roles):
        return tables
    else:
        shops_users = shop_user_crud.get_all_by_user_id(user_id=current_user.id)
        user_shops = [shop_user.shop_id for shop_user in shops_users]
        result_tables = []
        for table in tables:
            if table.shop_id in user_shops:
                result_tables.append(table)
        return result_tables


# Table name is used as an e-mail address for the order
@router.get("/name/{table_name}", response_model=UUID)
def get_shop_id_by_table_name(
    table_name: str, current_user: UsersTable = Depends(deps.get_current_active_table_moderator)
) -> UUID:
    table = table_crud.get_by_name(name=table_name)

    if not table:
        raise_status(HTTPStatus.NOT_FOUND, f"Table with name {table_name} not found")

    is_user_allowed_in_shop(user=current_user, shop_id=table.shop_id)
    return table.shop_id


@router.get("/{id}", response_model=TableSchema)
def get_by_id(id: UUID, current_user: UsersTable = Depends(deps.get_current_active_table_moderator)) -> TableSchema:
    table = table_crud.get(id)

    if not table:
        raise_status(HTTPStatus.NOT_FOUND, f"Table with id {id} not found")

    is_user_allowed_in_shop(user=current_user, shop_id=table.shop_id)
    return table


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(
    data: TableCreate = Body(...), current_user: UsersTable = Depends(deps.get_current_active_table_moderator)
) -> None:
    logger.info("Saving table", data=data)

    # I made it so only the table moderator create a table in a shop, but don't know if that is how you want it
    is_user_allowed_in_shop(user=current_user, shop_id=data.shop_id)

    table = table_crud.create(obj_in=data)
    return table


@router.put("/{table_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(
    *, table_id: UUID, item_in: TableUpdate, current_user: UsersTable = Depends(deps.get_current_active_table_moderator)
) -> Any:
    table = table_crud.get(id=table_id)
    logger.info("Updating table", data=table)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")

    is_user_allowed_in_shop(user=current_user, shop_id=item_in.shop_id)

    table = table_crud.update(
        db_obj=table,
        obj_in=item_in,
    )
    return table


@router.delete("/{table_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(table_id: UUID, current_user: UsersTable = Depends(deps.get_current_active_table_moderator)) -> None:
    table = table_crud.get(id=table_id)
    if not table:
        raise HTTPException(status_code=404, detail="Table not found")
    is_user_allowed_in_shop(user=current_user, shop_id=table.shop_id)

    return table_crud.delete(id=table_id)
