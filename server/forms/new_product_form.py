from typing import Any, List, Optional

import structlog
from pydantic import conlist, validator
from pydantic.class_validators import root_validator

from server.db.models import Kind, Strain, Tag
from server.pydantic_forms.core import FormPage, ReadOnlyField, register_form
from server.pydantic_forms.types import FormGenerator, State, SummaryData
from server.pydantic_forms.validators import Choice, LongText, MigrationSummary

logger = structlog.get_logger(__name__)


def validate_product_name(product_name: str, values: State) -> str:
    """Check if product already exists."""
    products = Kind.query.all()
    product_items = [item.name.lower() for item in products]
    if product_name.lower() in product_items:
        raise ValueError("Dit product bestaat al.")
    return product_name


def validate_strain_name(strain_name: str, values: State) -> str:
    """Check if strain already exists."""
    strains = Strain.query.all()
    strain_items = [item.name.lower() for item in strains]
    if strain_name.lower() in strain_items:
        raise ValueError("Deze kruising bestaat al.")
    return strain_name


def validate_multiple_strains(strain_names: List[str], values: State) -> List[str]:
    """Check if strains already exist."""
    strains = Strain.query.all()
    strain_items = [item.name.lower() for item in strains]

    invalid_strains = []

    for strain_name in strain_names:
        if strain_name.lower() in strain_items:
            invalid_strains.append(strain_name)

    if invalid_strains:
        raise ValueError(f"The following strains already exist: {', '.join(invalid_strains)}")

    return strain_names


def validate_combined_strains(cls, values):
    # If the value the same as its default value it returns None
    new_strain = (
        values.get("new_strain_from_name")
        if values.get("new_strain_from_name") is not None
        else cls.Config.new_strain_from_name_default
    )
    strain_count = len(values.get("strain_choice", [])) + len(values.get("create_new_strains", []))

    description_nl = values.get("product_description_nl") if values.get("product_description_nl") is not "" else None
    description_en = values.get("product_description_en") if values.get("product_description_en") is not "" else None
    has_full_description = bool(description_nl and description_en)

    if (strain_count == 0) and not new_strain and not has_full_description:
        raise ValueError(f'At least 1 strain required or check "New strain from name" or add EN/NL Descriptions')

    return values


def validate_tag_name(tag_name: str, values: State) -> str:
    """Check if tag already exists."""
    tags = Tag.query.all()
    tag_items = [item.name.lower() for item in tags]
    if tag_name.lower() in tag_items:
        raise ValueError("Deze tag bestaat al.")
    return tag_name


def create_strain_form(current_state: dict) -> FormGenerator:
    class StrainForm(FormPage):
        class Config:
            title = "Nieuwe kruising toevoegen"

        strain_name: str
        _validate_strain_name: classmethod = validator("strain_name", allow_reuse=True)(validate_strain_name)

    user_input = yield StrainForm
    return user_input.dict()


def create_tag_form(current_state: dict) -> FormGenerator:
    class TagForm(FormPage):
        class Config:
            title = "Nieuwe tag toevoegen"

        tag_name: str
        _validate_tag_name: classmethod = validator("tag_name", allow_reuse=True)(validate_tag_name)

    user_input = yield TagForm
    return user_input.dict()


class ProductType(Choice):
    """Product type as used in the create product form."""

    C = "CBD"
    H = "Hybrid"
    I = "Indica"
    S = "Sativa"


def create_product_form(current_state: dict) -> FormGenerator:
    # Setup summary
    summary_fields = [
        "product_name",
        "product_type",
    ]
    summary_labels = ["Wiet naam", "type"]

    def summary_data(user_input: dict[str, Any]) -> SummaryData:
        return {
            "labels": summary_labels,
            "columns": [[str(user_input[nm]) for nm in summary_fields]],
        }

    strains = Strain.query.all()

    StrainChoice = Choice(
        "StrainChoice",
        zip(
            [str(strain.id) for strain in strains],
            [(str(strain.id), strain.name) for strain in strains],
        ),  # type: ignore
    )

    # Todo: in future this could be implemented to pre-select a category in price template form
    # categories = Category.query.filter(Category.shop_id == UUID("19149768-691c-40d8-a08e-fe900fd23bc0")).all()
    #
    # CategoryChoice = Choice(
    #     "CategoryChoice",
    #     zip(
    #         [str(category.id) for category in categories],
    #         [(category.name, category.name) for category in categories],
    #     ),  # type: ignore
    # )

    class ProductForm(FormPage):
        class Config:
            title = "Nieuw cannabis product"
            new_strain_from_name_default = True
            gebruiken_default = True

        product_name: str
        product_type: ProductType
        product_description_nl: Optional[LongText]
        product_description_en: Optional[LongText]
        strain_choice: conlist(StrainChoice, min_items=0, max_items=3)
        create_new_strains: conlist(str, min_items=0, max_items=3, unique_items=True)
        new_strain_from_name: bool = Config.new_strain_from_name_default
        gebruiken: bool = Config.gebruiken_default

        _validate_product_name: classmethod = validator("product_name", allow_reuse=True)(validate_product_name)
        _validate_multiple_strains: classmethod = validator("create_new_strains", allow_reuse=True)(
            validate_multiple_strains
        )
        _validate_strains: classmethod = root_validator(pre=True, allow_reuse=True)(validate_combined_strains)

    user_input = yield ProductForm
    user_input_dict = user_input.dict()

    class SummaryForm(FormPage):
        class Config:
            title = "Samenvatting"

        class Summary(MigrationSummary):
            data = summary_data(user_input_dict)

        summary: Summary
        warning: str = ReadOnlyField(
            "Je kan (nog) geen producten bewerken. Zie je nu een 'typo' ga dan terug naar het vorige formulier en pas het aan."
        )

    _ = yield SummaryForm

    return user_input_dict


register_form("create_product_form", create_product_form)
register_form("create_strain_form", create_strain_form)
register_form("create_tag_form", create_tag_form)
