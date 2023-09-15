from http import HTTPStatus
from uuid import uuid4

import structlog

from server.utils.json import json_dumps


def test_license_get_multi(license_1, license_2, test_client, superuser_token_headers):
    response = test_client.get("/api/licenses", headers=superuser_token_headers)

    assert HTTPStatus.OK == response.status_code
    licenses = response.json()

    assert 2 == len(licenses)


def test_license_get_by_id(license_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/licenses/{license_1.id}", headers=superuser_token_headers)
    print(response.__dict__)
    assert HTTPStatus.OK == response.status_code
    license = response.json()
    assert license["name"] == "john"


def test_license_get_by_id_404(license_1, test_client, superuser_token_headers):
    response = test_client.get(f"/api/licenses/{str(uuid4())}", headers=superuser_token_headers)
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_license_save(test_client, superuser_token_headers):
    body = {"name": "New License"}

    response = test_client.post("/api/licenses/create", data=json_dumps(body), headers=superuser_token_headers)
    print(response)
    assert HTTPStatus.CREATED == response.status_code
    licenses = test_client.get("/api/licenses", headers=superuser_token_headers).json()
    assert 1 == len(licenses)


def test_license_update(license_1, test_client, superuser_token_headers):
    body = {"name": "Updated License"}
    response = test_client.put(f"/api/licenses/edit/{license_1.id}", data=json_dumps(body), headers=superuser_token_headers)
    assert HTTPStatus.CREATED == response.status_code

    response_updated = test_client.get(f"/api/licenses/{license_1.id}", headers=superuser_token_headers)
    license = response_updated.json()
    assert license["name"] == "Updated License"


def test_license_delete(license_1, test_client, superuser_token_headers):
    response = test_client.delete(f"/api/licenses/delete/{license_1.id}", headers=superuser_token_headers)
    print(response.content)
    assert HTTPStatus.NO_CONTENT == response.status_code
    licenses = test_client.get("/api/licenses", headers=superuser_token_headers).json()
    assert 0 == len(licenses)
