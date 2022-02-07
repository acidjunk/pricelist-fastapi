from typing import Optional
from uuid import UUID

from sqlalchemy.orm import contains_eager, defer

from server.crud.base import CRUDBase
from server.db.models import ShopToPrice
from server.schemas.shop_to_price import ShopToPriceCreate, ShopToPriceUpdate
from server.utils.json import json_dumps


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

    def get_products_with_prices_by_shop_id(self, *, shop_id: UUID):
        products = (
            ShopToPrice.query.join(ShopToPrice.price)
            .options(contains_eager(ShopToPrice.price), defer("price_id"))
            .filter(ShopToPrice.shop_id == shop_id)
            .all()
        )
        return products


shop_to_price_crud = CRUDShopToPrice(ShopToPrice)
