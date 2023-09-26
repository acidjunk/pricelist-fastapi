from http import HTTPStatus
from typing import Any, List, Optional
from uuid import UUID

from fastapi import APIRouter
from fastapi.param_functions import Body, Depends
from starlette.responses import Response

from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_license import license_crud
from server.schemas.license import LicenseCreate, LicenseSchema, LicenseUpdate

router = APIRouter()


@router.get("/", response_model=List[LicenseSchema])
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[LicenseSchema]:
    licenses, header_range = license_crud.get_multi(
        skip=common["skip"], limit=common["limit"], filter_parameters=common["filter"], sort_parameters=common["sort"]
    )
    response.headers["Content-Range"] = header_range
    return licenses


@router.get("/{id}", response_model=LicenseSchema)
def get_by_id(id: UUID) -> LicenseSchema:
    license = license_crud.get(id)
    if not license:
        raise_status(HTTPStatus.NOT_FOUND, f"License with id {id} not found")
    return license


@router.get("/name/{name}", response_model=LicenseSchema)
def get_by_name(name: str) -> LicenseSchema:
    license = license_crud.get_by_name(name=name)

    if not license:
        raise_status(HTTPStatus.NOT_FOUND, f"License with name {name} not found")
    return license


@router.post("/create", response_model=None, status_code=HTTPStatus.CREATED)
def create(data: LicenseCreate) -> None:
    license = license_crud.create(obj_in=data)
    return license


@router.put("/edit/{id}", response_model=None, status_code=HTTPStatus.CREATED)
def edit(id: UUID, data: LicenseUpdate) -> Any:
    license = license_crud.get(id)
    if not license:
        raise_status(HTTPStatus.NOT_FOUND, f"License with id {id} not found")
    license = license_crud.update(db_obj=license, obj_in=data)
    return license


@router.delete("/delete/{id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(id: UUID) -> None:
    return license_crud.delete(id=id)
