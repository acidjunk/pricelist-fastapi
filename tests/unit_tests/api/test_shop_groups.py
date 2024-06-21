from http import HTTPStatus
from uuid import uuid4

import pytest
import structlog

from server.utils.json import json_dumps

logger = structlog.get_logger(__name__)


def test_shop_groups_get_multi(test_client, shop_group_1, shop_group_2, superuser_token_headers):
    response = test_client.get("/api/shop-groups", headers=superuser_token_headers)
    assert HTTPStatus.OK == response.status_code
    shop_groups = response.json()
    # Shop group Maastricht is inserted automatically by the DB data migration
    assert 3 == len(shop_groups)


def test_shop_group_get_by_id(shop_group_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/shop-groups/{shop_group_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.OK == response.status_code
    shop_group = response.json()
    assert shop_group["name"] == "ShopGroup1"


def test_shop_group_get_by_id_404(test_client, superuser_token_headers):
    response = test_client.get(f"/api/shop-groups/{str(uuid4())}", headers=superuser_token_headers)
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_shop_group_get_by_name(shop_group_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/shop-groups/name/{shop_group_1.name}", headers=superuser_token_headers)
    assert HTTPStatus.OK == response.status_code
    shop_group = response.json()
    assert shop_group["name"] == "ShopGroup1"


def test_shop_group_get_by_name_404(test_client, superuser_token_headers):
    response = test_client.get(f"/api/shop-groups/name/{str(uuid4())}", headers=superuser_token_headers)
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_shop_group_save(test_client, superuser_token_headers):
    body = {"name": "ShopGroup3", "shop_ids": [str(uuid4()), str(uuid4())]}
    response = test_client.post("/api/shop-groups/", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code
    shop_groups = test_client.get("/api/shop-groups", headers=superuser_token_headers).json()
    assert 2 == len(shop_groups)


def test_shop_group_update(shop_group_1, test_client, superuser_token_headers):
    body = {"name": "Updated Group", "shop_ids": shop_group_1.shop_ids}
    response = test_client.put(
        f"/api/shop-groups/{shop_group_1.id}", data=json_dumps(body), headers=superuser_token_headers
    )
    assert HTTPStatus.CREATED == response.status_code
    response_updated = test_client.get(f"/api/shop-groups/{shop_group_1.id}", headers=superuser_token_headers)
    shop_group = response_updated.json()
    assert shop_group["name"] == "Updated Group"


def test_shop_group_delete(shop_group_1, test_client, superuser_token_headers):
    response = test_client.delete(f"/api/shop-groups/{shop_group_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.NO_CONTENT == response.status_code
    shop_groups = test_client.get("/api/shop-groups", headers=superuser_token_headers).json()
    assert 1 == len(shop_groups)
