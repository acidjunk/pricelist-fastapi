from typing import Optional
from uuid import UUID

from server.crud.base import CRUDBase
from server.db.models import ShopToPrice
from server.schemas.shop_to_price import ShopToPriceCreate, ShopToPriceUpdate


class CRUDShopToPrice(CRUDBase[ShopToPrice, ShopToPriceCreate, ShopToPriceUpdate]):
    def check_relation_by_kind(self, *, shop_id: UUID, price_id: UUID, kind_id: UUID) -> Optional[ShopToPrice]:
        check_query = (
            ShopToPrice.query.filter_by(shop_id=shop_id).filter_by(price_id=price_id).filter_by(kind_id=kind_id).all()
        )
        return check_query

    def check_relation_by_product(self, *, shop_id: UUID, price_id: UUID, product_id: UUID) -> Optional[ShopToPrice]:
        check_query = (
            ShopToPrice.query.filter_by(shop_id=shop_id)
            .filter_by(price_id=price_id)
            .filter_by(product_id=product_id)
            .all()
        )
        return check_query


shop_to_price_crud = CRUDShopToPrice(ShopToPrice)
