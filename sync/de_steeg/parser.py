import json
import uuid

import structlog
from more_itertools import one

from server.db.models import Kind
from sync.de_steeg.schemas import Product, Price
from sync.de_steeg.settings import sync_settings

from server.db import db

logger = structlog.get_logger(__name__)


class ProductNotFoundException(Exception):
    pass


ONE_GRAM_ENDINGS = ["1 g", "1 gr", "1 gra", "1 gram"]
TWO_GRAM_ENDINGS = ["2 g", "2 gr", "2 gra", "2 gram"]
FIVE_GRAM_ENDINGS = ["5 g", "5 gr", "5 gra", "5 gram"]
JOINT_ENDINGS = ["j", "join", "joint"]


def check_endings(name: str, endings: list[str]) -> bool:
    for ending in endings:
        if name.lower().endswith(ending):
            return True
    return False


# noinspection PyPackageRequirements
class Parser:
    def __init__(self, json_data):
        self.parsed = False
        self.json_data = data

        self.products = []
        self.prices = []
        self.prices_without_product = []
        self.parse()

    def parse(self):
        logger.info("Parsing data", number_of_items=len(self.json_data["data"]))
        for key, item in self.json_data["data"].items():
            if item["type"] == "gewicht_teller":
                product = Product(product_id=key, name=item["naam"], amount=item["aantal"])
                self.products.append(product)

        for key, item in self.json_data["data"].items():
            price_flavor_warning = None
            if item["type"] == "verkoop_artikel":
                price = Price(
                    price_id=key,
                    name=item["naam"],
                    base=item["basis"],
                    minimal=item["minimal"],
                    price=item["prijs"],
                    amount=item["aantal"],
                )
                # try to find the amount
                if check_endings(price.name, ONE_GRAM_ENDINGS):
                    price.one = True
                elif check_endings(price.name, TWO_GRAM_ENDINGS):
                    price.two = True
                elif check_endings(price.name, FIVE_GRAM_ENDINGS):
                    price.five = True
                elif check_endings(price.name, JOINT_ENDINGS):
                    price.joint = True
                else:
                    price_flavor_warning = f"Couldn't parse {price.name} to a correct price_flavor"
                # try to resolve the product, so Prices "know" to which product they belong
                product_id = self.get_product_id(item["naam"])
                if product_id:
                    if price_flavor_warning and sync_settings.LOG_PRODUCT_WARNINGS:
                        logger.warning(price_flavor_warning)
                    price.product_id = product_id
                    price.product_name = one([p.name for p in self.products if p.product_id == product_id])
                    self.prices.append(price)
                else:
                    self.prices_without_product.append(price)
        logger.info(
            "Parsed data",
            products=len(self.products),
            prices=len(self.prices),
            prices_without_product=len(self.prices_without_product),
        )
        self.parsed = True
        if sync_settings.LOG_PRODUCT_WARNINGS:
            logger.warning(
                "Prices without a root product",
                prices_without_product=self.prices_without_product,
                number_of_prices_without_product=len(self.prices_without_product),
            )

    def get_product_id(self, name: str):
        for product in self.products:
            if name.startswith(product.name):
                return product.product_id
        if sync_settings.ALLOW_ROOTLESS_PRODUCTS:
            return None
        raise ProductNotFoundException(f"Could not find product with name {name}")

    def sync_products(self):
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


if __name__ == "__main__":
    with open(sync_settings.JSON_FILE_LOCATION, "r") as file:
        data = json.load(file)
    parser = Parser(data)
    # parser.sync_products()
    parser.sync_products()
