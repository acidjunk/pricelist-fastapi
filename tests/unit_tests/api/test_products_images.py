from http import HTTPStatus
from uuid import uuid4

import pytest
import structlog

from server.utils.json import json_dumps

logger = structlog.getLogger(__name__)


def test_product_image_update(product_3, test_client, superuser_token_headers):
    body = {
        "name": "Test Product",
        "short_description_nl": "Test Product description",
        "description_nl": "Test Product description",
        "short_description_en": "Test Product description",
        "description_en": "Test Product description",
        "complete": False,
        "image_1": "test-product-1-1.png",
        "image_2": "test-product-2-1.png",
        "image_3": {"src": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA", "title": "new-image.png"},
        "image_4": None,
        "image_5": None,
        "image_6": None,
    }
    response = test_client.put(
        f"/api/products-images/{product_3.id}", data=json_dumps(body), headers=superuser_token_headers
    )
    assert HTTPStatus.CREATED == response.status_code

    response_updated = test_client.get(f"/api/products/{product_3.id}", headers=superuser_token_headers)
    product = response_updated.json()
    assert product["image_3"] == "test-product-3-2.png"


def test_product_image_delete(product_3, test_client, superuser_token_headers):
    body = {"image": "image_3"}

    response = test_client.put(
        f"/api/products-images/delete/{product_3.id}", data=json_dumps(body), headers=superuser_token_headers
    )
    assert HTTPStatus.CREATED == response.status_code

    response_updated = test_client.get(f"/api/products/{product_3.id}", headers=superuser_token_headers)
    product = response_updated.json()
    assert product["image_3"] is None
