import structlog

from server.api.api_v1.router_fix import APIRouter
from server.api.helpers import create_presigned_url

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/{file_name}")
def get_signed_download_link(file_name: str):
    download_link = create_presigned_url(file_name)
    return download_link
