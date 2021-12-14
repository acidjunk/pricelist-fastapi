from datetime import datetime
from typing import Optional
from uuid import UUID

from server.schemas.base import BoilerplateBaseModel


class KindToFlavorBase(BoilerplateBaseModel):
    id: Optional[UUID]
    kind_id: UUID
    flavor_id: UUID

    class Config:
        orm_mode = True


# Properties to receive via API on creation
class KindToFlavorCreate(KindToFlavorBase):
    pass


# Properties to receive via API on update
class KindToFlavorUpdate(KindToFlavorBase):
    pass


class KindToFlavorInDBBase(KindToFlavorBase):
    class Config:
        orm_mode = True


# Additional properties to return via API
class KindToFlavorSchema(KindToFlavorInDBBase):
    pass
