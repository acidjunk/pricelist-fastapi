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
from server.api.helpers import create_presigned_url, delete_from_temporary_bucket, move_between_buckets

logger = structlog.get_logger(__name__)
router = APIRouter()


@router.get("/signed-url/{image_name}")
def get_signed_url(image_name: str):
    image_url = create_presigned_url(image_name)
    return image_url


@router.post("/move")
def move_images():
    return move_between_buckets()


@router.post("/delete-temp")
def delete_temporary_images():
    return delete_from_temporary_bucket()
