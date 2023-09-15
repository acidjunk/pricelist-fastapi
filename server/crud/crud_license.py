from typing import Optional

from server.crud.base import CRUDBase
from server.db.models import License
from server.schemas.license import LicenseCreate, LicenseUpdate


class CRUDLicense(CRUDBase[License, LicenseUpdate, LicenseCreate]):
    def get_by_name(self, *, name: str) -> Optional[License]:
        return License.query.filter(License.name == name).first()


license_crud = CRUDLicense(License)
