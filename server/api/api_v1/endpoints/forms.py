from http import HTTPStatus
from typing import Any
from uuid import UUID

from fastapi.routing import APIRouter
from pydantic_forms.core import list_forms, start_form

import server.forms  # noqa -> Needed to register all forms

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
    state = start_form(form_key, user_inputs=json_data, user="Just a user")

    return state