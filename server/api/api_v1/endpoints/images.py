from datetime import datetime
from http import HTTPStatus
from typing import Any, List
from uuid import UUID

import structlog
from server.api.api_v1.router_fix import APIRouter
from server.api.helpers import create_presigned_url, move_between_buckets

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/signed-url/{image_name}")
def get_signed_url(image_name: str):
    image_url = create_presigned_url(image_name)
    return image_url


@router.post("/move")
def move_images():
    return move_between_buckets()
