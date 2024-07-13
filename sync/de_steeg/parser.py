import json
import uuid

import structlog
from more_itertools import one

from server.db.models import Kind, Category
from sync.de_steeg.schemas import Product, Price, Weight, JsonPriceField
from sync.de_steeg.settings import sync_settings

from server.db import db
from server.db.models import Price as PriceModel

logger = structlog.get_logger(__name__)


class ProductNotFoundException(Exception):
    pass


JOINT_ENDINGS = ["j", "join", "joint"]


def check_endings(name: str, endings: list[str]) -> bool:
    for ending in endings:
        if name.lower().endswith(ending):
            return True
    return False


def float_to_label(quantity: float) -> str:
    if quantity.is_integer():
        return str(int(quantity))
    else:
        # Otherwise, convert the float to a string and replace the decimal point with a comma
        return str(quantity).replace(".", ",")


def get_price_field(price: Price, pre_rolled: bool = False) -> JsonPriceField:
    quantity = price.weight[0].weight
    label = "joint"
    if not pre_rolled:
        # Todo: sum weights ?
        label = f"{float_to_label(quantity)} gram"
    price_field = JsonPriceField(price=price.price, label=label, quantity=quantity, active=True)
    return price_field


# noinspection PyPackageRequirements
class Parser:
    def __init__(self, json_data):
        self.parsed = False
        self.json_data = data

        self.products = []
        self.prices = []
        self.prices_without_product = []
        self.price_names_skipped = []
        self.categories = []
        self.parse()

    def parse(self):
        logger.info("Parsing data", number_of_items=len(self.json_data["data"]))
        for key, item in self.json_data["data"].items():
            if item["type"] == "gewicht_teller":
                product = Product(product_id=int(key.replace("#", "")), name=item["naam"], amount=item["aantal"])
                self.products.append(product)

        for key, item in self.json_data["data"].items():
            price_flavor_warning = None
            if item["type"] == "verkoop_artikel":
                gewicht = item["gewicht"]
                assert len(gewicht) == 3, "All items should have 3 weight indicators"
                if gewicht[0]["gewichtLink1"] == 0:
                    if sync_settings.LOG_PRODUCT_WARNINGS:
                        logger.warning("Skipping product", product=item["naam"])
                    self.price_names_skipped.append(item["naam"])
                    continue
                price = Price(
                    price_id=key,
                    category=item["omzetgroep"],
                    name=item["naam"],
                    base=item["basis"],
                    minimal=item["minimal"],
                    price=item["prijs"],
                    amount=item["aantal"],
                    weight=[
                        Weight(product_id=gewicht[0]["gewichtLink1"], weight=gewicht[0]["grammen"]),
                        Weight(product_id=gewicht[1]["gewichtLink2"], weight=gewicht[0]["grammen"]),
                        Weight(product_id=gewicht[2]["gewichtLink3"], weight=gewicht[0]["grammen"]),
                    ],
                )
                if check_endings(price.name, JOINT_ENDINGS):
                    price.joint = True
                # Todo: find out how to handle edibles

                # try to resolve the product, so Prices "know" to which product they belong
                product_id = self.get_product_id(price)
                if product_id:
                    if price_flavor_warning and sync_settings.LOG_PRODUCT_WARNINGS:
                        logger.warning(price_flavor_warning)
                    price.product_id = product_id
                    price.product_name = one([p.name for p in self.products if p.product_id == product_id])
                    self.prices.append(price)
                else:
                    self.prices_without_product.append(price)

        self.categories = list(set([price.category for price in self.prices]))
        self.parsed = True
        logger.info(
            "Parsed data",
            categories=self.categories,
            products=len(self.products),
            prices=len(self.prices),
            prices_without_product=len(self.prices_without_product),
            prices_skipped=len(self.price_names_skipped),
        )
        if sync_settings.LOG_PRODUCT_WARNINGS:
            logger.warning(
                "Prices without a root product",
                prices_without_product=self.prices_without_product,
                number_of_prices_without_product=len(self.prices_without_product),
                names_skipped=self.price_names_skipped,
            )

    def get_product_id(self, price: Price):
        for product in self.products:
            if product.product_id == price.weight[0].product_id:
                return product.product_id
        if sync_settings.ALLOW_ROOTLESS_PRODUCTS:
            return None
        raise ProductNotFoundException(f"Could not find product with name {price.name}")

    def sync_products(self):
        logger.info(f"Syncing products to database", products=len(self.products))
        for product in self.products:
            # check if product exists:
            if len(Kind.query.filter_by(name=product.name).all()) == 1:
                logger.info(f"Skipping product {product.name}: already exists")
            else:
                logger.info(f"Adding product {product.name} to database")
                kind_id = str(uuid.uuid4())
                kind = Kind(
                    id=kind_id,
                    name=product.name,
                    c=False,
                    h=False,
                    i=False,
                    s=False,
                    short_description_nl=f"{product.product_id}: {product.name}",
                    description_nl="",
                    short_description_en=f"{product.product_id}: {product.name}",
                    description_en="",
                )
                db.session.add(kind)
                db.session.commit()
                # db.session.add(fixture)
                # record = KindToTag(id=str(uuid.uuid4()), kind_id=fixture_id, tag=tag_1, amount=90)
                # db.session.add(record)
                # record = KindToFlavor(id=str(uuid.uuid4()), kind_id=fixture_id, flavor_id=flavor_1.id)
                # db.session.add(record)
                # record = KindToStrain(id=str(uuid.uuid4()), kind_id=fixture_id, strain_id=strain_1.id)

    def sync_categories(self):
        logger.info(f"Syncing categories to database", categories=len(self.categories))
        for category in self.categories:
            # check if category exists:
            if len(Category.query.filter_by(name=category).all()) == 1:
                logger.info(f"Skipping category {category}: already exists")
            else:
                logger.info(f"Adding category {category} to database")
                category_id = str(uuid.uuid4())
                record = Category(
                    id=category_id,
                    main_category_id=sync_settings.DEFAULT_CATEGORY_ID,
                    name=category,
                    name_en=category,
                    description=category,
                    shop_id=sync_settings.SHOP_ID,
                    cannabis=True,
                )
                db.session.add(record)
                db.session.commit()

    def sync_prices(self):
        logger.info(f"Syncing prices to database", categories=len(self.products))
        for product in self.products:
            prices = [p for p in self.prices if p.product_id == product.product_id]

            # handle all price variations
            pre_rolled = [get_price_field(p, pre_rolled=True) for p in prices if p.joint]
            cannabis = [get_price_field(p) for p in prices if not p.joint]
            # todo: edibles, they are now added to the cannabis field
            edibles = []

            logger.info(f"Syncing prices for {product.name} to database", pre_rolled=pre_rolled, cannabis=cannabis)

            # Todo
            # check if price exists:
            # Todo: check which flags and prices or only product_id (not sure if that will be unique enough)

            # Todo: flag "#23" -> Edibles

            # Create a price
            price_id = str(uuid.uuid4())
            price = PriceModel(
                id=price_id,
                internal_product_id=product.product_id,
                pre_rolled_joints=[p.dict() for p in pre_rolled],
                cannabis=[p.dict() for p in cannabis],
                edible=[p.dict() for p in edibles],
                shop_group_id=sync_settings.SHOP_GROUP_ID,
            )
            db.session.add(price)
            db.session.commit()
            # logger.info(
            #     f"Synced prices for {product.name} to database",
            #     id=str(price.id),
            #     internal_product_id=price.internal_product_id,
            #     one=price.one,
            #     two_five=price.two_five,
            #     five=price.five,
            #     joint=price.joint,
            # )


if __name__ == "__main__":
    with open(sync_settings.JSON_FILE_LOCATION, "r") as file:
        data = json.load(file)
    parser = Parser(data)
    parser.sync_products()
    parser.sync_categories()
    parser.sync_prices()
