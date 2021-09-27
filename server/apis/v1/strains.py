import uuid
from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi.param_functions import Body
from fastapi.routing import APIRouter
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.api.models import delete, save, update
from server.crud.crud_strain import strain_crud
from server.db import Strain
from server.schemas.product import Product, ProductCreate, ProductUpdate
import structlog

from server.schemas.strain import StrainCreate, StrainSchema

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/")
def get_multi_strains(response: Response, common: dict = Depends(common_parameters)) -> List[StrainSchema]:
    strains, header_range = strain_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range
    return strains


@router.post("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def save_strain(data: StrainCreate = Body(...)) -> None:
    logger.info("Saving strain", data=data)
    return save(Strain, data)
