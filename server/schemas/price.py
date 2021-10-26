from uuid import UUID
from datetime import datetime
from server.schemas.base import BoilerplateBaseModel


class PriceBase(BoilerplateBaseModel):
    id: UUID
    name: str
    description: str

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class PriceCreate(PriceBase):
    pass


# Properties to receive via API on update
class PriceUpdate(PriceBase):
    pass


class PriceInDBBase(PriceBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class PriceSchema(PriceInDBBase):
    pass
