from server.crud.base import CRUDBase
from server.db.models import Flavor
from server.schemas.flavor import FlavorCreate, FlavorUpdate


class CRUDFlavor(CRUDBase[Flavor, FlavorCreate, FlavorUpdate]):
    pass


flavor_crud = CRUDFlavor(Flavor)
