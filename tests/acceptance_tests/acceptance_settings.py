from typing import Optional

from pydantic import BaseSettings
from pydantic.networks import AnyHttpUrl
from pydantic import validator

SUFFIX: str = "/v1"


class AcceptanceSettings(BaseSettings):
    BASE_ACC_BACKEND_URI: AnyHttpUrl = "https://api.staging.prijslijst.info"
    ACC_BACKEND_URI = BASE_ACC_BACKEND_URI + SUFFIX
    BASE_PRD_BACKEND_URI: AnyHttpUrl = "https://api.prijslijst.info"
    PRD_BACKEND_URI = BASE_PRD_BACKEND_URI + SUFFIX

    @validator("BASE_ACC_BACKEND_URI", pre=False)
    def validate_url(cls, v: str):
        if v.count('/') > 2:
            raise ValueError("please dont use suffixes")
        return v

if __name__ == "__main__":
    settings = AcceptanceSettings(BASE_ACC_BACKEND_URI="https://api.staging.prijslijst.info//")