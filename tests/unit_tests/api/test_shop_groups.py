from http import HTTPStatus
from uuid import uuid4

import pytest
import structlog

from server.utils.json import json_dumps

logger = structlog.get_logger(__name__)

# Sample test data
sample_shop_group_data = {"name": "ShopGroup1", "shop_ids": ["123", "456"]}


# Test cases


def test_shop_groups_get_multi(shop_group_1, shop_group_2, test_client, superuser_token_headers):
    response = test_client.get("/api/shop_groups", headers=superuser_token_headers)
    assert HTTPStatus.OK == response.status_code
    shop_groups = response.json()
    assert 2 == len(shop_groups)


def test_shop_group_get_by_id(shop_group_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/shop_groups/{shop_group_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.OK == response.status_code
    shop_group = response.json()
    assert shop_group["name"] == "ShopGroup1"


def test_shop_group_get_by_id_404(test_client, superuser_token_headers):
    response = test_client.get(f"/api/shop_groups/{str(uuid4())}", headers=superuser_token_headers)
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_shop_group_get_by_name(shop_group_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/shop_groups/name/{shop_group_1.name}", headers=superuser_token_headers)
    assert HTTPStatus.OK == response.status_code
    shop_group = response.json()
    assert shop_group["name"] == "ShopGroup1"


def test_shop_group_get_by_name_404(test_client, superuser_token_headers):
    response = test_client.get(f"/api/shop_groups/name/{str(uuid4())}", headers=superuser_token_headers)
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_shop_group_save(test_client, superuser_token_headers):
    body = sample_shop_group_data
    response = test_client.post("/api/shop_groups/", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code
    shop_groups = test_client.get("/api/shop_groups", headers=superuser_token_headers).json()
    assert 1 == len(shop_groups)


def test_shop_group_update(shop_group_1, test_client, superuser_token_headers):
    body = {"name": "Updated Group", "shop_ids": ["789"]}
    response = test_client.put(
        f"/api/shop_groups/{shop_group_1.id}", data=json_dumps(body), headers=superuser_token_headers
    )
    assert HTTPStatus.CREATED == response.status_code
    response_updated = test_client.get(f"/api/shop_groups/{shop_group_1.id}", headers=superuser_token_headers)
    shop_group = response_updated.json()
    assert shop_group["name"] == "Updated Group"


def test_shop_group_delete(shop_group_1, test_client, superuser_token_headers):
    response = test_client.delete(f"/api/shop_groups/{shop_group_1.id}", headers=superuser_token_headers)
    assert HTTPStatus.NO_CONTENT == response.status_code
    shop_groups = test_client.get("/api/shop_groups", headers=superuser_token_headers).json()
    assert 0 == len(shop_groups)
