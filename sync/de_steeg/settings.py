from pydantic import BaseSettings


class SyncSettings(BaseSettings):
    """
    Deal with global sync settings.

    The goal is to provide some sensible default for developers here. All constants can be
    overloaded via ENV vars. The validators are used to ensure that you get readable error
    messages when an ENV var isn't correctly formated; for example when you provide an incorrect
    formatted DATABASE_URI.

    ".env" loading is also supported. FastAPI will autoload and ".env" file if one can be found
    """

    PROJECT_NAME: str = "Steeg"
    TESTING: bool = True
    JSON_FILE_LOCATION: str = "sync/de_steeg/data/csj1.json"
    SHOP_ID: str = "470f3f5a-e7b9-43a5-bbfd-2ffce8c161e4"
    SHOP_GROUP_ID: str = "655f89b0-a456-413c-b14a-412038088f2d"
    DEFAULT_CATEGORY_ID: str = "549ced87-e698-4100-83ca-b95c0a0275f7"
    ALLOW_ROOTLESS_PRODUCTS: bool = True
    LOG_PRODUCT_WARNINGS: bool = False


sync_settings = SyncSettings()
