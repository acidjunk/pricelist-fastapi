from http import HTTPStatus
from uuid import uuid4
import structlog
from server.db import Strain
from server.utils.json import json_dumps

logger = structlog.getLogger(__name__)


def test_strains_get_multi(strain_1, strain_2, test_client):
    response = test_client.get("/api/strains")

    assert HTTPStatus.OK == response.status_code
    strains = response.json()

    assert 2 == len(strains)


def test_strain_get_by_id(strain_1, test_client):
    response = test_client.get(f"/api/strains/{strain_1}")
    print(response.__dict__)
    assert HTTPStatus.OK == response.status_code
    strain = response.json()
    assert strain["id"] == "63b21ceb-23ce-494b-8767-9b0b2a81f1b4"


def test_strain_get_by_id_404(strain_1, test_client):
    response = test_client.get(f"/api/strains/{str(uuid4())}")
    assert HTTPStatus.NOT_FOUND == response.status_code


def test_strain_save(test_client):
    body = {"id": "3b21ceb-23ce-494b-8767-9b0b2a81f1b4", "name": "New Strain"}

    response = test_client.post(
        "/api/strains/",
        data=json_dumps(body),
        headers={"Content_Type": "application/json"},
    )
    assert HTTPStatus.NO_CONTENT == response.status_code
    strains = test_client.get("/api/strains").json()
    assert 1 == len(strains)


def test_strain_update(strain_1, test_client):
    body = {"id": strain_1, "name": "Updated Strain"}
    response = test_client.put(
        f"/api/strains/{strain_1}",
        data=json_dumps(body),
        headers={"Content_Type": "application/json"},
    )
    assert HTTPStatus.NO_CONTENT == response.status_code

    response_updated = test_client.get(f"/api/strains/{strain_1}")
    strain = response_updated.json()
    assert strain["name"] == "Updated Strain"


def test_strain_delete(strain_1, test_client):
    response = test_client.delete(f"/api/strains/{strain_1}")
    assert HTTPStatus.NO_CONTENT == response.status_code
    assert len(Strain.query.all()) == 0
