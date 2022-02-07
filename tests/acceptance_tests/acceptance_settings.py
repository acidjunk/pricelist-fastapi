import os
from typing import Dict, Optional

import requests
from dotenv import load_dotenv
from pydantic import BaseSettings, validator
from pydantic.networks import AnyHttpUrl

SUFFIX: str = "/v1/"


def acceptance_superuser_headers(acc_backend_uri) -> Dict[str, str]:
    login_data = {"username": os.environ.get("ADMIN_USER"), "password": os.environ.get("ADMIN_PASSWORD")}
    r = requests.post(acc_backend_uri + "login/access-token", data=login_data)
    tokens = r.json()
    a_token = tokens["access_token"]
    headers = {"Authorization": f"Bearer {a_token}"}
    return headers


class AcceptanceSettings(BaseSettings):
    load_dotenv()
    BASE_ACC_BACKEND_URI: AnyHttpUrl = os.environ.get("BASE_ACC_BACKEND_URI") or "https://api.staging.prijslijst.info"
    ACC_BACKEND_URI = BASE_ACC_BACKEND_URI + SUFFIX
    BASE_PRD_BACKEND_URI: AnyHttpUrl = os.environ.get("BASE_PRD_BACKEND_URI") or "https://api.prijslijst.info"
    PRD_BACKEND_URI = BASE_PRD_BACKEND_URI + SUFFIX
    ACC_SUPERUSER_TOKEN_HEADERS = acceptance_superuser_headers(ACC_BACKEND_URI)

    @validator("BASE_ACC_BACKEND_URI", pre=False)
    def validate_url(cls, v: str):
        if v.count("/") > 2:
            raise ValueError("please dont use suffixes")
        return v


acceptance_settings = AcceptanceSettings()


if __name__ == "__main__":
    print(acceptance_settings.PRD_BACKEND_URI)
    print(acceptance_settings.ACC_BACKEND_URI)
