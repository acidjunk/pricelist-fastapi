from http import HTTPStatus
from typing import List, Optional
from uuid import UUID

from fastapi.param_functions import Body
from fastapi.routing import APIRouter

from server.api.error_handling import raise_status
from server.api.models import delete, save, update
from server.db import Strain
from server.schemas.product import Product, ProductCreate, ProductUpdate
import structlog

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/")
def fetch(strain_type: Optional[str] = None):
    query = Strain.query
    return query.all()
