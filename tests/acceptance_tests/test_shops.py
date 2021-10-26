from urllib.request import urlopen
import requests

from tests.acceptance_tests.conftest import PRD_BACKEND_URI, ACC_BACKEND_URI


def test_shops():
    response_flask = requests.get(PRD_BACKEND_URI + "shops")
    response_fastapi = requests.get(ACC_BACKEND_URI + "shops")

    assert response_fastapi == response_flask


