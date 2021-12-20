# Copyright 2019-2020 SURF.
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

"""Module that implements process related API endpoints."""

from fastapi import Depends

from server.api import deps
from server.api.api_v1.endpoints import (
    categories_images,
    flavors,
    health,
    kinds,
    kinds_to_flavors,
    kinds_to_strains,
    kinds_to_tags,
    login,
    prices,
    products,
    shops,
    shops_to_prices,
    strains,
    users,
)
from server.api.api_v1.router_fix import APIRouter
from server.websockets import chat

# Todo: add security depends here or in endpoints

api_router = APIRouter()

api_router.include_router(login.router, tags=["login"])
api_router.include_router(health.router, prefix="/health", tags=["system"])
api_router.include_router(shops.router, prefix="/shops", tags=["shops"])
api_router.include_router(shops_to_prices.router, prefix="/shops-to-prices", tags=["shops-to-prices"])
api_router.include_router(
    categories_images.router,
    prefix="/categories-images",
    tags=["categories-images"],
    dependencies=[Depends(deps.get_current_active_superuser)],
)
api_router.include_router(
    products.router, prefix="/products", tags=["products"], dependencies=[Depends(deps.get_current_active_superuser)]
)  # todo handle auth in edpoint itself (id is fetachable; rest is admin)
api_router.include_router(
    kinds.router, prefix="/kinds", tags=["kinds"]
)  # todo handle auth in edpoint itself (id is fetachable; rest is admin)
api_router.include_router(
    kinds_to_flavors.router,
    prefix="/kinds-to-flavors",
    tags=["kinds-relations"],
    dependencies=[Depends(deps.get_current_active_superuser)],
)
api_router.include_router(
    kinds_to_strains.router,
    prefix="/kinds-to-strains",
    tags=["kinds-relations"],
    dependencies=[Depends(deps.get_current_active_superuser)],
)
api_router.include_router(
    kinds_to_tags.router,
    prefix="/kinds-to-tags",
    tags=["kinds-relations"],
    dependencies=[Depends(deps.get_current_active_superuser)],
)
api_router.include_router(
    strains.router, prefix="/strains", tags=["strains"], dependencies=[Depends(deps.get_current_active_superuser)]
)
api_router.include_router(
    flavors.router, prefix="/flavors", tags=["flavors"], dependencies=[Depends(deps.get_current_active_superuser)]
)
api_router.include_router(
    prices.router, prefix="/prices", tags=["prices"], dependencies=[Depends(deps.get_current_active_superuser)]
)
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
