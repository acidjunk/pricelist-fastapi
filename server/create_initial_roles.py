# Copyright 2024 René Dohmen <acidjunk@gmail.com>
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
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
