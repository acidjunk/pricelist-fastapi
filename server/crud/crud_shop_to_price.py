from server.crud.base import CRUDBase
from server.db.models import ShopToPrice
from server.schemas.shop_to_price import ShopToPriceCreate, ShopToPriceUpdate


class CRUDShopToPrice(CRUDBase[ShopToPrice, ShopToPriceCreate, ShopToPriceUpdate]):
    pass


shop_to_price_crud = CRUDShopToPrice(ShopToPrice)
