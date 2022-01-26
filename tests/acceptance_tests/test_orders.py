from urllib.request import urlopen

import requests
from deepdiff import DeepDiff  # For Deep Difference of 2 objects
from deepdiff import DeepHash  # For hashing objects based on their contents
from deepdiff import DeepSearch, grep  # For finding if item exists in an object

from server.utils.json import json_dumps
from tests.acceptance_tests.acceptance_settings import acceptance_settings
from tests.acceptance_tests.helpers import get_difference_in_json_list

PRD_BACKEND_URI = acceptance_settings.PRD_BACKEND_URI
ACC_BACKEND_URI = acceptance_settings.ACC_BACKEND_URI


def test_orders_get_multi():
    response_prd = requests.get(PRD_BACKEND_URI + "orders?range=%5B0%2C200%5D").json()
    response_acc = requests.get(ACC_BACKEND_URI + "orders?skip=0&limit=200").json()
    ddiff = DeepDiff(response_acc, response_prd, ignore_order=True)
    assert ddiff == {}
