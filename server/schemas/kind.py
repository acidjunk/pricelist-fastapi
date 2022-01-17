from datetime import datetime
from typing import List, Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class KindBase(BoilerplateBaseModel):
    name: str
    short_description_nl: Optional[str] = None
    description_nl: Optional[str] = None
    short_description_en: Optional[str] = None
    description_en: Optional[str] = None
    c: bool = False
    h: bool = False
    i: bool = False
    s: bool = False
    complete: bool = False
    approved: bool = False
    approved_by: Optional[str] = None
    disapproved_reason: Optional[str] = None
    image_1: Optional[str] = None
    image_2: Optional[str] = None
    image_3: Optional[str] = None
    image_4: Optional[str] = None
    image_5: Optional[str] = None
    image_6: Optional[str] = None


# Properties to receive via API on creation
class KindCreate(KindBase):
    pass


# Properties to receive via API on update
class KindUpdate(KindBase):
    pass


class KindInDBBase(KindBase):
    id: UUID
    created_at: datetime
    modified_at: Optional[datetime] = None
    approved_at: Optional[datetime] = None

    class Config:
        orm_mode = True


# Additional properties to return via API
class KindSchema(KindInDBBase):
    pass


class KindWithDetails(KindInDBBase):
    # Todo: Georgi investigate if it's ok to use the "ModelSchema" here. It has DB write access which isn't needed
    # We could be more strict and generic by re-using the schema of tag, flavors etc. instead of `List[dict]`
    tags: List[dict]
    tags_amount: int = 0
    flavors: List[dict]
    flavors_amount: int = 0
    strains: List[dict]
    strains_amount: int = 0
    prices: Optional[List[dict]] = None


class KindWithDetailsAndPrices(KindWithDetails):
    prices: List[dict] = []
