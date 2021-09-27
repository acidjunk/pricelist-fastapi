from server.crud.base import CRUDBase
from server.db.models import Strain
from server.schemas.strain import StrainCreate, StrainUpdate


class CRUDStrain(CRUDBase[Strain, StrainCreate, StrainUpdate]):
    pass


strain_crud = CRUDStrain(Strain)
