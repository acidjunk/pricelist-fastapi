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
import structlog

from server.api.api_v1.router_fix import APIRouter
from server.api.helpers import create_download_url
from server.utils.auth import send_download_link_email

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/{file_name}")
def get_signed_download_link(file_name: str):
    download_link = create_download_url(file_name, 7200)
    return download_link


@router.post("/send")
def send_download_link_via_email(file_name: str, email: str, shop_name: str):
    link = create_download_url(file_name, 604799)
    send_download_link_email(email, link, shop_name)
