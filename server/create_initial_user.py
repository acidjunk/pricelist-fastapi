import structlog

from server.crud import user_crud
from server.crud.crud_role import role_crud
from server.crud.crud_role_user import role_user_crud
from server.schemas import UserCreate, RoleCreate
from server.schemas.role_user import RoleUserCreate
from server.settings import app_settings

logger = structlog.get_logger(__name__)


def main() -> None:
    logger.info("Creating initial data")
    superuser = user_crud.get_by_email(email=app_settings.FIRST_SUPERUSER)
    logger.info("suser" + str(superuser))
    role_admin = role_crud.get_by_name(name=app_settings.FIRST_SUPERUSER_ROLE)
    logger.info("role_admin" + str(role_admin))
    if not role_admin:
        role_in = RoleCreate(
            name=app_settings.FIRST_SUPERUSER_ROLE,
            description=app_settings.FIRST_SUPERUSER_ROLE_DESCRIPTION
        )
        logger.info("role_in" + str(role_in))
        role_admin = role_crud.create(obj_in=role_in)
        logger.info("role_admin" + str(role_admin))
        logger.info("Initial role created")
    else:
        logger.info("Skipping role creation: role already exists")

    if not superuser:
        user_in = UserCreate(
            email=app_settings.FIRST_SUPERUSER,
            username=app_settings.FIRST_SUPERUSER,
            password=app_settings.FIRST_SUPERUSER_PASSWORD,
        )
        logger.info("userIN" + str(user_in))
        superuser = user_crud.create(obj_in=user_in)  # noqa: F841
        logger.info("superuser" + str(superuser))
        role_user_in = RoleUserCreate(
            user_id=superuser.id,
            role_id=role_admin.id
        )
        logger.info("role_user_in" + str(role_user_in))
        role_admin_superuser = role_user_crud.create(obj_in=role_user_in)
        logger.info("role_admin_superuser" + str(role_admin_superuser))
        logger.info("Initial superuser created")
    else:
        logger.info("Skipping creation: superuser already exists")



if __name__ == "__main__":
    main()
