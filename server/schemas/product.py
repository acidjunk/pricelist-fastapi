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
from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel
from server.schemas.price import DefaultPrice


class ProductEmptyBase(BoilerplateBaseModel):
    pass


class ProductBase(BoilerplateBaseModel):
    name: str
    short_description_nl: Optional[str] = None
    description_nl: Optional[str] = None
    short_description_en: Optional[str] = None
    description_en: Optional[str] = None
    complete: bool = False
    shop_group_id: Optional[UUID] = None
    image_1: Union[Optional[dict], Optional[str]]
    image_2: Union[Optional[dict], Optional[str]]
    image_3: Union[Optional[dict], Optional[str]]
    image_4: Union[Optional[dict], Optional[str]]
    image_5: Union[Optional[dict], Optional[str]]
    image_6: Union[Optional[dict], Optional[str]]


# Properties to receive via API on creation
class ProductCreate(ProductBase):
    pass


# Properties to receive via API on update
class ProductUpdate(ProductBase):
    modified_at: Optional[datetime] = None


class ProductInDBBase(ProductBase):
    id: UUID
    created_at: datetime
    modified_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class ProductSchema(ProductInDBBase):
    approved: bool = False
    approved_by: Optional[str] = None
    disapproved_reason: Optional[str] = None


class ProductWithDetails(ProductInDBBase):
    images_amount: int = 0


class ProductWithDefaultPrice(ProductWithDetails):
    # to be the same with the Flask backend
    prices: Optional[DefaultPrice] = DefaultPrice()


class ProductWithDetailsAndPrices(ProductWithDetails):
    prices: List[dict] = []


class ProductImageDelete(ProductEmptyBase):
    image: str
