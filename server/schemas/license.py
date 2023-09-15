from pydantic import BaseModel
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class LicenseBase(BoilerplateBaseModel):
    name: str


class LicenseCreate(LicenseBase):
    pass


class LicenseUpdate(LicenseBase):
    pass


class LicenseInDB(LicenseBase):
    id: UUID

    class Config:
        orm_mode = True


class LicenseSchema(LicenseInDB):
    pass
