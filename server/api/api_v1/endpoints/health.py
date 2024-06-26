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

import structlog
from sqlalchemy.exc import OperationalError

from server.api.api_v1.router_fix import APIRouter
from server.api.error_handling import raise_status
from server.crud.crud_user import user_crud
from server.db import ProductsTable
from server.schemas import UserCreate
from server.settings import app_settings

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=str)
def get_health() -> str:
    try:
        ProductsTable.query.limit(1).value(ProductsTable.name)
    except OperationalError as e:
        logger.warning("Health endpoint returned: notok!")
        logger.debug("Health endpoint error details", error=str(e))
        raise_status(HTTPStatus.INTERNAL_SERVER_ERROR)
    return "OK"


@router.get("/ping")
def pong():
    """
    Sanity check.
    This will let the user know that the service is operational.
    And this path operation will:
    * show a lifesign
    """
    return {"ping": "pong!"}
