# Copyright 2019-2020 SURF.
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
import base64
import os
from http import HTTPStatus
from typing import List, Optional

import boto3 as boto3
from more_itertools import chunked
from sqlalchemy import String, cast
from sqlalchemy.orm import Query
from sqlalchemy.sql import expression
from starlette.responses import Response
from structlog import get_logger

from server.api.error_handling import raise_status
from server.db.database import BaseModel

logger = get_logger(__name__)

# Todo: decide if we need this
VALID_SORT_KEYS = {
    "id": "id",
    "name": "name",
    "created": "created_at",
    "creator": "created_by",
    "modifier": "modified_by",
    "modified": "modified_at",
}

s3 = boto3.resource(
    "s3",
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)


def _query_with_filters(
    response: Response,
    model: BaseModel,
    query: Query,
    range: Optional[List[int]] = None,
    sort: Optional[List[str]] = None,
    filters: Optional[List[str]] = None,
) -> List:
    if filters is not None:
        for filter in chunked(filters, 2):
            if filter and len(filter) == 2:
                field = filter[0]
                value = filter[1]
                value_as_bool = value.lower() in (
                    "yes",
                    "y",
                    "ye",
                    "true",
                    "1",
                    "ja",
                    "insync",
                )
                if value is not None:
                    if field.endswith("_gt"):
                        query = query.filter(model.__dict__[field[:-3]] > value)
                    elif field.endswith("_gte"):
                        query = query.filter(model.__dict__[field[:-4]] >= value)
                    elif field.endswith("_lte"):
                        query = query.filter(model.__dict__[field[:-4]] <= value)
                    elif field.endswith("_lt"):
                        query = query.filter(model.__dict__[field[:-3]] < value)
                    elif field.endswith("_ne"):
                        query = query.filter(model.__dict__[field[:-3]] != value)
                    elif field == "tsv":
                        logger.debug("Running full-text search query.", value=value)
                        query = query.search(value)
                    elif field in model.__dict__:
                        query = query.filter(cast(model.__dict__[field], String).ilike("%" + value + "%"))

    if sort is not None and len(sort) >= 2:
        for sort in chunked(sort, 2):
            if sort and len(sort) == 2:
                if sort[1].upper() == "DESC":
                    query = query.order_by(expression.desc(model.__dict__[sort[0]]))
                else:
                    query = query.order_by(expression.asc(model.__dict__[sort[0]]))

    if range is not None and len(range) == 2:
        try:
            range_start = int(range[0])
            range_end = int(range[1])
            assert range_start < range_end
        except (ValueError, AssertionError):
            msg = "Invalid range parameters"
            logger.exception(msg)
            raise_status(HTTPStatus.BAD_REQUEST, msg)
        total = query.count()
        query = query.slice(range_start, range_end)

        response.headers["Content-Range"] = f"items {range_start}-{range_end}/{total}"

    return query.all()


def upload_file(blob, file_name):
    image_mime, image_base64 = blob.split(",")
    image = base64.b64decode(image_base64)

    # Todo: make dynamic
    s3_object = s3.Object("images-georgi-prijslijst-info", file_name)
    resp = s3_object.put(Body=image, ContentType="image/png")

    if resp["ResponseMetadata"]["HTTPStatusCode"] == 200:
        logger.info("Uploaded file to S3", file_name=file_name)

        # Make the result public
        object_acl = s3_object.Acl()
        response = object_acl.put(ACL="public-read")
        logger.info("Made public", response=response)


def name_file(column_name, record_name, image_name=""):
    _, _, image_number = column_name.rpartition("_")[0:3]
    current_name = image_name
    extension = "png"  # todo: make it dynamic e.g. get it from mime-type, extra arg for this function?
    if not current_name:
        name = "".join([c if c.isalnum() else "-" for c in record_name])
        name = f"{name}-{image_number}-1".lower()
    else:
        name, _ = current_name.split(".")
        name, _, counter = name.rpartition("-")[0:3]
        name = f"{name}-{int(counter) + 1}".lower()
    name = f"{name}.{extension}"
    logger.info("Named file", col_name=column_name, name_in=image_name, name_out=name)
    return name


#
#
# def invalidateShopCache(shop_id):
#     item = load(Shop, shop_id)
#     item.modified_at = datetime.utcnow()
#     try:
#         save(item)
#     except Exception as e:
#         abort(500, f"Error: {e}")
