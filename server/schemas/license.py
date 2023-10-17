from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel

from server.schemas.base import BoilerplateBaseModel


class LicenseBase(BoilerplateBaseModel):
    name: str
    start_date: datetime
    end_date: Optional[datetime]
    improviser_user: UUID
    is_recurring: bool
    seats: float
    order_id: UUID


class LicenseCreate(LicenseBase):
    pass


class LicenseUpdate(BoilerplateBaseModel):
    seats: float
    end_date: datetime


class LicenseInDB(LicenseBase):
    id: UUID
    modified_at: datetime
    created_at: datetime

    class Config:
        orm_mode = True


class LicenseSchema(LicenseInDB):
    pass
