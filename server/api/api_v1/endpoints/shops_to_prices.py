from http import HTTPStatus
from typing import List, Any
from uuid import UUID
import os

from fastapi.routing import APIRouter
from fastapi.param_functions import Body, Depends
from fastapi import HTTPException
from starlette.responses import Response
from server.api.deps import common_parameters
from server.api.error_handling import raise_status
from server.crud.crud_shop import shop_crud
import structlog
import boto3
import json

from server.schemas.shop import ShopCreate, ShopUpdate, ShopBase

logger = structlog.get_logger(__name__)

router = APIRouter()


@router.post("/sendmessage", status_code=HTTPStatus.NO_CONTENT)
def sendmessage() -> str:
    dynamo = boto3.client('dynamodb', aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), region_name='eu-central-1')
    URL = "https://1n1v00okbh.execute-api.eu-central-1.amazonaws.com/prod"
    client = boto3.client("apigatewaymanagementapi", endpoint_url=URL, aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"), aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"), region_name='eu-central-1')

    connectionIds = dynamo.scan(TableName="websocket_ids")
    for connection in connectionIds["Items"]:
        msg = {"message": "Hello " + str(connection["connectionId"]["S"])}
        response = client.post_to_connection(ConnectionId=connection["connectionId"]["S"], Data=json.dumps(msg))
        print(response)
    return "message sent !"

@router.get("/")
def get_multi(response: Response, common: dict = Depends(common_parameters)) -> List[ShopBase]:
    shops, header_range = shop_crud.get_multi(
        skip=common["skip"],
        limit=common["limit"],
        filter_parameters=common["filter"],
        sort_parameters=common["sort"],
    )
    response.headers["Content-Range"] = header_range
    return shops


@router.get("/{id}", response_model=ShopBase)
def get_by_id(id: UUID) -> ShopBase:
    shop = shop_crud.get(id)
    if not shop:
        raise_status(HTTPStatus.NOT_FOUND, f"Shop with id {id} not found")
    return shop


@router.post("/", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def create(data: ShopCreate = Body(...)) -> None:
    logger.info("Saving shop", data=data)
    return shop_crud.create(obj_in=data)


@router.put("/{shop_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def update(*, shop_id: UUID, item_in: ShopUpdate) -> Any:
    shop = shop_crud.get(id=shop_id)
    logger.info("shop", data=shop)
    if not shop:
        raise HTTPException(status_code=404, detail="Shop not found")

    shop = shop_crud.update(
        db_obj=shop,
        obj_in=item_in,
    )
    return shop


@router.delete("/{shop_id}", response_model=None, status_code=HTTPStatus.NO_CONTENT)
def delete(shop_id: UUID) -> None:
    return shop_crud.delete(id=shop_id)
