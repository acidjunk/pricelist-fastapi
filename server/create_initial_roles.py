import structlog

from server.crud.crud_role import role_crud
from server.schemas import RoleCreate

logger = structlog.get_logger(__name__)

roles = [
    RoleCreate(name="admin", description="God Mode!"),
    RoleCreate(name="moderator", description="Can moderate other users' content"),
    RoleCreate(name="staff", description="Can assign employees to shops and disable/enable employees"),
    RoleCreate(name="operator", description="Can create and block users"),
    RoleCreate(name="employee", description="Can see orders and enable/disable products for shops"),
    RoleCreate(name="table_moderator", description="Can create and edit tables for a specific shop"),
]


def main() -> None:
    logger.info("Creating initial roles")
    for role in roles:
        existing_role = role_crud.get_by_name(name=role.name)
        if not existing_role:
            role_crud.create(obj_in=role)
            logger.info("Initial role created")
        else:
            logger.info("Skipping role creation: role already exists")


if __name__ == "__main__":
    main()
