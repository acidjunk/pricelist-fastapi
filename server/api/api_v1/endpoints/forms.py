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
from http import HTTPStatus
from typing import Any, Optional
from uuid import UUID

from fastapi.routing import APIRouter

import server.forms  # noqa -> Needed to register all forms
from server.pydantic_forms.core import list_forms, start_form

router = APIRouter()


@router.get("", response_model=list[str])
def get_forms() -> list[str]:
    """
    Retrieve all forms.

    Args:
        response: Response

    Returns:
        Form titles

    """
    return list_forms()


@router.post("/{form_key}", response_model=dict, status_code=HTTPStatus.CREATED)
async def new_form(
    form_key: str,
    json_data: list[dict[str, Any]],
    shop_id: Optional[UUID] = None,
    # user: OIDCUserModel or None = Depends(),  # type: ignore
) -> dict[str, UUID]:
    # Todo: determine what to do with user?

    # match json_data:
    #     case [{"ticket_id": ticket_id, "next_process_state": next_process_state}, *user_inputs]:
    #         ticket = await get_ticket(ticket_id)
    #         ticket_transition = TicketTransitionSchema(ticket=ticket, next_process_state=next_process_state)
    #         state = start_form(
    #             form_key, user_inputs=user_inputs, user="Just a user", ticket_transition=ticket_transition
    #         )
    #     case _ as user_inputs:
    state = start_form(form_key, user_inputs=json_data, user="Just a user", extra_state={"shop_id": shop_id})

    return state
