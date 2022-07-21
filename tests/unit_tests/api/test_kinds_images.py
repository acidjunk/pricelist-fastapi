from http import HTTPStatus
from uuid import uuid4

import pytest
import structlog

from server.utils.json import json_dumps

logger = structlog.getLogger(__name__)


def test_kind_image_update(kind_3, test_client, superuser_token_headers):
    body = {
        "name": "Test Kind",
        "short_description_nl": "Test Kind description",
        "description_nl": "Test Kind description",
        "short_description_en": "Test Kind description",
        "description_en": "Test Kind description",
        "c": False,
        "h": False,
        "i": False,
        "s": True,
        "complete": False,
        "image_1": "test-kind-1-1.png",
        "image_2": "test-kind-2-1.png",
        "image_3": {"src": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA", "title": "new-image.png"},
        "image_4": None,
        "image_5": None,
        "image_6": None,
    }
    response = test_client.put(f"/api/kinds-images/{kind_3.id}", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code

    response_updated = test_client.get(f"/api/kinds/{kind_3.id}", headers=superuser_token_headers)
    kind = response_updated.json()
    assert kind["image_3"] == "test-kind-3-2.png"


def test_kind_image_delete(kind_3, test_client, superuser_token_headers):
    body = {"image": "image_3"}

    response = test_client.put(
        f"/api/kinds-images/delete/{kind_3.id}", data=json_dumps(body), headers=superuser_token_headers
    )
    assert HTTPStatus.CREATED == response.status_code

    response_updated = test_client.get(f"/api/kinds/{kind_3.id}", headers=superuser_token_headers)
    kind = response_updated.json()
    assert kind["image_3"] is None
