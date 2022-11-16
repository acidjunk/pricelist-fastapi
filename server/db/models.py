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

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Optional
from xmlrpc.client import DateTime

import pytz
import sqlalchemy
import structlog
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text, TypeDecorator, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.engine import Dialect
from sqlalchemy.exc import DontWrapMixin
from sqlalchemy.orm import backref, relationship
from sqlalchemy_utils import UUIDType

from server.db.database import BaseModel, Database
from server.settings import app_settings
from server.utils.date_utils import nowtz

# from server.db import db


logger = structlog.get_logger(__name__)

TAG_LENGTH = 20
STATUS_LENGTH = 255

db = Database(app_settings.DATABASE_URI)


class UtcTimestampException(Exception, DontWrapMixin):
    pass


class UtcTimestamp(TypeDecorator):
    """Timestamps in UTC.

    This column type always returns timestamps with the UTC timezone, regardless of the database/connection time zone
    configuration. It also guards against accidentally trying to store Python naive timestamps (those without a time
    zone).
    """

    impl = sqlalchemy.types.TIMESTAMP(timezone=True)

    def process_bind_param(self, value: Optional[datetime], dialect: Dialect) -> Optional[datetime]:
        if value is not None:
            if value.tzinfo is None:
                raise UtcTimestampException(f"Expected timestamp with tzinfo. Got naive timestamp {value!r} instead")
        return value

    def process_result_value(self, value: Optional[datetime], dialect: Dialect) -> Optional[datetime]:
        if value is not None:
            return value.astimezone(timezone.utc)
        return value


class RolesUsersTable(BaseModel):
    __tablename__ = "roles_users"
    id = Column(Integer(), primary_key=True)
    user_id = Column("user_id", UUID(as_uuid=True), ForeignKey("user.id"))
    role_id = Column("role_id", UUID(as_uuid=True), ForeignKey("role.id"))


# What RoleMixin does ?
# class Role(BaseModel, RoleMixin):
class RolesTable(BaseModel):
    __tablename__ = "role"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(80), unique=True)
    description = Column(String(255))

    # __str__ is required by Flask-Admin, so we can have human-readable values for the Role when editing a User.
    def __str__(self):
        return self.name

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.name)


# Same here
class UsersTable(BaseModel):
    __tablename__ = "user"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String(255), unique=True)
    first_name = Column(String(255), index=True)
    last_name = Column(String(255), index=True)
    username = Column(String(255), unique=True)
    password = Column(String(255))
    active = Column(Boolean())
    fs_uniquifier = Column(String(255))
    created_at = Column(DateTime, default=datetime.utcnow)
    confirmed_at = Column(DateTime())
    roles = relationship("RolesTable", secondary="roles_users", backref=backref("users", lazy="dynamic"))

    mail_offers = Column(Boolean, default=False)

    # Human-readable values for the User when editing user related stuff.
    def __str__(self):
        return f"{self.username} : {self.email}"

    # __hash__ is required to avoid the exception TypeError: unhashable type: 'Role' when saving a User
    def __hash__(self):
        return hash(self.email)

    @property
    def is_active(self):
        """Returns `True` if the user is active."""
        return self.active

    @property
    def is_superuser(self):
        """Returns `True` if the user is a member of the admin role."""
        print(self.roles)
        for role in self.roles:
            if role.name == "admin":
                return True
        return False


class Tag(BaseModel):
    __tablename__ = "tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(60), unique=True, index=True)

    kinds_to_tags = relationship("KindToTag", cascade="save-update, merge, delete")

    def __repr__(self):
        return self.name


class Flavor(BaseModel):
    __tablename__ = "flavors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(60), unique=True, index=True)
    icon = Column(String(60), unique=True, index=True)
    color = Column(String(20), default="#000000")

    kinds_to_flavors = relationship("KindToFlavor", cascade="save-update, merge, delete")

    def __repr__(self):
        return self.name


class Shop(BaseModel):
    __tablename__ = "shops"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(String(255), unique=True)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow())
    last_pending_order = Column(String(255), unique=True)  # order id of last pending order for this shop (UUID)
    last_completed_order = Column(String(255), unique=True)  # order id of last completed order for this shop (UUID)
    allowed_ips = Column(JSON)
    shops_to_price = relationship("ShopToPrice", cascade="save-update, merge, delete")
    shop_to_category = relationship("Category", cascade="save-update, merge, delete")

    def __repr__(self):
        return self.name


class Table(BaseModel):
    __tablename__ = "shop_tables"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255))
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    shop = relationship("Shop", lazy=True)

    def __repr__(self):
        return f"{self.shop.name}: {self.name}"


class MainCategory(BaseModel):
    __tablename__ = "main_categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255))
    name_en = Column(String(255), nullable=True)
    icon = Column(String(60), nullable=True)
    description = Column(String(255), unique=True, index=True)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    shop = relationship("Shop", lazy=True)
    order_number = Column(Integer, default=0)

    def __repr__(self):
        return f"{self.shop.name}: {self.name}"


class Category(BaseModel):
    __tablename__ = "categories"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    main_category_id = Column(
        "main_category_id", UUID(as_uuid=True), ForeignKey("main_categories.id"), nullable=True, index=True
    )
    main_category = relationship("MainCategory", lazy=True)
    color = Column(String(20), default="#376E1A")
    name = Column(String(255))
    name_en = Column(String(255), nullable=True)
    icon = Column(String(60), nullable=True)
    description = Column(String(255), unique=True, index=True)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    shop = relationship("Shop", lazy=True)
    order_number = Column(Integer, default=0)
    cannabis = Column(Boolean, default=False)
    image_1 = Column(String(255), unique=True, index=True)
    image_2 = Column(String(255), unique=True, index=True)

    shops_to_price = relationship("ShopToPrice", cascade="save-update, merge, delete")

    def __repr__(self):
        main_category = self.main_category.name if self.main_category_id else "NO_MAIN"
        return f"{self.shop.name}: {main_category}: {self.name}"


class Kind(BaseModel):
    __tablename__ = "kinds"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), unique=True, index=True)
    short_description_nl = Column(String())
    description_nl = Column(String())
    short_description_en = Column(String())
    description_en = Column(String())
    c = Column(Boolean(), default=False)
    h = Column(Boolean(), default=False)
    i = Column(Boolean(), default=False)
    s = Column(Boolean(), default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    complete = Column("complete", Boolean(), default=False)
    approved_at = Column(DateTime)
    approved = Column("approved", Boolean(), default=False)
    approved_by = Column("approved_by", UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    disapproved_reason = Column(String())
    kind_tags = relationship("Tag", secondary="kinds_to_tags")
    kind_to_tags = relationship("KindToTag", cascade="save-update, merge, delete")
    kind_flavors = relationship("Flavor", secondary="kinds_to_flavors")
    kind_to_flavors = relationship("KindToFlavor", cascade="save-update, merge, delete")
    image_1 = Column(String(255), unique=True, index=True)
    image_2 = Column(String(255), unique=True, index=True)
    image_3 = Column(String(255), unique=True, index=True)
    image_4 = Column(String(255), unique=True, index=True)
    image_5 = Column(String(255), unique=True, index=True)
    image_6 = Column(String(255), unique=True, index=True)

    shop_to_price = relationship("ShopToPrice", cascade="save-update, merge, delete")

    kind_strains = relationship("Strain", secondary="kinds_to_strains")
    kind_to_strains = relationship("KindToStrain", cascade="save-update, merge, delete")

    def __repr__(self):
        return "<Kinds %r, id:%s>" % (self.name, self.id)


class Price(BaseModel):
    __tablename__ = "prices"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    internal_product_id = Column("internal_product_id", String(), unique=True)
    half = Column("half", Float(), nullable=True)
    one = Column("one", Float(), nullable=True)
    two_five = Column("two_five", Float(), nullable=True)
    five = Column("five", Float(), nullable=True)
    joint = Column("joint", Float(), nullable=True)
    piece = Column("piece", Float(), nullable=True)

    def __repr__(self):
        return f"Price for product_id: {self.internal_product_id}"


class Order(BaseModel):
    __tablename__ = "orders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    customer_order_id = Column(Integer)
    notes = Column(String, nullable=True)
    shop_id = Column(UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    table_id = Column(UUID(as_uuid=True), ForeignKey("shop_tables.id"), nullable=True)
    order_info = Column(JSON)
    total = Column(Float())
    status = Column(String(), default="pending")
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_by = Column("completed_by", UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    completed_at = Column(DateTime, nullable=True)

    shop = relationship("Shop", lazy=True)
    user = relationship("UsersTable", backref=backref("orders", uselist=False))
    table = relationship("Table", backref=backref("shop_tables", uselist=False))

    def __repr__(self):
        return "<Order for shop: %s with total: %s>" % (self.shop.name, self.total)


# Tag many to many relations
class KindToTag(BaseModel):
    __tablename__ = "kinds_to_tags"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    amount = Column("amount", Integer(), default=0)
    kind_id = Column("kind_id", UUID(as_uuid=True), ForeignKey("kinds.id"), index=True)
    tag_id = Column("tag_id", UUID(as_uuid=True), ForeignKey("tags.id"), index=True)
    kind = relationship("Kind", lazy=True)
    tag = relationship("Tag", lazy=True)


# Flavor many to many relation
class KindToFlavor(BaseModel):
    __tablename__ = "kinds_to_flavors"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    kind_id = Column("kind_id", UUID(as_uuid=True), ForeignKey("kinds.id"), index=True)
    flavor_id = Column("flavor_id", UUID(as_uuid=True), ForeignKey("flavors.id"), index=True)
    kind = relationship("Kind", lazy=True)
    flavor = relationship("Flavor", lazy=True)

    def __repr__(self):
        return f"{self.flavor.name}: {self.kind.name}"


class KindToStrain(BaseModel):
    __tablename__ = "kinds_to_strains"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    kind_id = Column("kind_id", UUID(as_uuid=True), ForeignKey("kinds.id"), index=True)
    strain_id = Column("strain_id", UUID(as_uuid=True), ForeignKey("strains.id"), index=True)
    kind = relationship("Kind", lazy=True)
    strain = relationship("Strain", lazy=True)

    def __repr__(self):
        return f"{self.strain.name}: {self.kind.name}"


class ProductsTable(BaseModel):
    __tablename__ = "products"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), index=True)
    short_description_nl = Column(String())
    description_nl = Column(String())
    short_description_en = Column(String())
    description_en = Column(String())
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    complete = Column("complete", Boolean(), default=False)
    approved_at = Column(DateTime)
    approved = Column("approved", Boolean(), default=False)
    approved_by = Column("approved_by", UUID(as_uuid=True), ForeignKey("user.id"), nullable=True)
    disapproved_reason = Column(String())
    image_1 = Column(String(255), unique=True, index=True)
    image_2 = Column(String(255), unique=True, index=True)
    image_3 = Column(String(255), unique=True, index=True)
    image_4 = Column(String(255), unique=True, index=True)
    image_5 = Column(String(255), unique=True, index=True)
    image_6 = Column(String(255), unique=True, index=True)

    shop_to_price = relationship("ShopToPrice", cascade="save-update, merge, delete")


class ShopToPrice(BaseModel):
    __tablename__ = "shops_to_price"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    active = Column("active", Boolean(), default=True)
    new = Column("new", Boolean(), default=False)
    shop_id = Column("shop_id", UUID(as_uuid=True), ForeignKey("shops.id"), index=True)
    shop = relationship("Shop", lazy=True)
    category_id = Column("category_id", UUID(as_uuid=True), ForeignKey("categories.id"), nullable=True, index=True)
    category = relationship("Category", lazy=True)
    kind_id = Column("kind_id", UUID(as_uuid=True), ForeignKey("kinds.id"), index=True, nullable=True)
    kind = relationship("Kind", lazy=True)
    product_id = Column("product_id", UUID(as_uuid=True), ForeignKey("products.id"), index=True, nullable=True)
    product = relationship("ProductsTable", lazy=True)
    price_id = Column("price_id", UUID(as_uuid=True), ForeignKey("prices.id"), index=True)
    price = relationship("Price", lazy=True)
    use_half = Column("use_half", Boolean(), default=True)
    use_one = Column("use_one", Boolean(), default=True)
    use_two_five = Column("two_five", Boolean(), default=True)
    use_five = Column("use_five", Boolean(), default=True)
    use_joint = Column("use_joint", Boolean(), default=True)
    use_piece = Column("use_piece", Boolean(), default=True)
    order_number = Column(Integer, default=0)
    joint_grams = Column(Float, default=0)
    piece_grams = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    modified_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class Strain(BaseModel):
    __tablename__ = "strains"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    #
    # def __repr__(self):
    #     return self.name


# user_datastore = SQLAlchemySessionUserDatastore(db.session, User, Role)
