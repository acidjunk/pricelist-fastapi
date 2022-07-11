from http import HTTPStatus
from typing import Any, List, Optional
from uuid import UUID

import structlog
from fastapi import HTTPException
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api import deps
from server.api.api_v1.router_fix import APIRouter
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_kind import kind_crud
from server.db.models import UsersTable
from server.schemas.kind import (
    KindCreate,
    KindSchema,
    KindUpdate,
    KindWithDefaultPrice,
    KindWithDetails,
    KindWithDetailsAndPrices,
)

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.get("/", response_model=List[KindWithDefaultPrice])
def get_multi(
    response: Response,
    common: dict = Depends(common_parameters),
    current_user: UsersTable = Depends(deps.get_current_active_superuser),
) -> List[KindWithDefaultPrice]:
    kinds, header_range = kind_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range

    for kind in kinds:
        kind.tags = [
            {"id": tag.id, "name": f"{tag.tag.name}: {tag.amount}", "amount": tag.amount} for tag in kind.kind_to_tags
        ]
        kind.tags_amount = len(kind.tags)
        kind.flavors = [
            {"id": flavor.id, "name": flavor.flavor.name, "icon": flavor.flavor.icon, "color": flavor.flavor.color}
            for flavor in kind.kind_to_flavors
        ]
        kind.flavors_amount = len(kind.flavors)
        kind.strains = [{"id": strain.id, "name": f"{strain.strain.name}"} for strain in kind.kind_to_strains]
        kind.strains_amount = len(kind.strains)
        kind.images_amount = 0
        for i in [1, 2, 3, 4, 5, 6]:
            if getattr(kind, f"image_{i}"):
                kind.images_amount += 1

    return kinds


@router.get("/{id}", response_model=KindWithDetailsAndPrices)
def get_by_id(id: UUID, shop: Optional[UUID] = None) -> KindWithDetailsAndPrices:
    kind = kind_crud.get(id)
    if not kind:
        raise_status(HTTPStatus.NOT_FOUND, f"Kind with id {id} not found")

    kind.prices = []
    if shop:
        for price_relation in kind.shop_to_price:
            if price_relation.shop_id == shop:
                kind.prices.append(
                    {
                        "id": price_relation.price.id,
                        "internal_product_id": price_relation.price.internal_product_id,
                        "active": price_relation.active,
                        "new": price_relation.new,
                        # In flask's serializer there is no half
                        # "half": price_relation.price.half if price_relation.use_half else None,
                        "one": price_relation.price.one if price_relation.use_one else None,
                        "two_five": price_relation.price.two_five if price_relation.use_two_five else None,
                        "five": price_relation.price.five if price_relation.use_five else None,
                        "joint": price_relation.price.joint if price_relation.use_joint else None,
                        "piece": price_relation.price.piece if price_relation.use_piece else None,
                        "created_at": price_relation.created_at,
                        "modified_at": price_relation.modified_at,
                    }
                )

    kind.tags = [
        {"id": tag.id, "name": tag.tag.name, "amount": tag.amount}
        for tag in sorted(kind.kind_to_tags, key=lambda i: i.amount, reverse=True)
    ]
    kind.tags_amount = len(kind.tags)

    kind.flavors = [
        {"id": flavor.id, "name": flavor.flavor.name, "icon": flavor.flavor.icon, "color": flavor.flavor.color}
        for flavor in sorted(kind.kind_to_flavors, key=lambda i: i.flavor.name)
    ]
    kind.flavors_amount = len(kind.flavors)

    kind.strains = [
        {"id": strain.id, "name": strain.strain.name}
        for strain in sorted(kind.kind_to_strains, key=lambda i: i.strain.name)
    ]
    kind.strains_amount = len(kind.strains)

    kind.images_amount = 0
    for i in [1, 2, 3, 4, 5, 6]:
        if getattr(kind, f"image_{i}"):
            kind.images_amount += 1

    return kind


@router.post("/", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: KindCreate = Body(...), current_user: UsersTable = Depends(deps.get_current_active_superuser)) -> None:
    logger.info("Saving kind", data=data)
    kind = kind_crud.create(obj_in=data)
    return kind


@router.put("/{kind_id}", response_model=None, status_code=HTTPStatus.CREATED)
def update(
    *, kind_id: UUID, item_in: KindUpdate, current_user: UsersTable = Depends(deps.get_current_active_superuser)
) -> Any:
    kind = kind_crud.get(id=kind_id)
    logger.info("Updating kind", data=kind)
    if not kind:
        raise HTTPException(status_code=404, detail="Kind not found")

    kind = kind_crud.update(
        db_obj=kind,
        obj_in=item_in,
    )
    return kind


@router.delete("/{kind_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(kind_id: UUID, current_user: UsersTable = Depends(deps.get_current_active_superuser)) -> None:
    return kind_crud.delete(id=kind_id)
