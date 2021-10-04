from urllib.request import urlopen
import requests

from tests.acceptance_tests.conftest import url_flask, url_fastapi


def test_shops():
    response_flask = requests.get(url_flask + "shops")
    response_fastapi = requests.get(url_fastapi + "shops")

    assert response_fastapi == response_flask


