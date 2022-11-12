from typing import Any

import structlog
from pydantic import conlist, validator
from pydantic_forms.core import FormPage, ReadOnlyField, register_form
from pydantic_forms.types import FormGenerator, State, SummaryData
from pydantic_forms.validators import Choice, MigrationSummary

from server.db.models import Kind, Strain

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


def create_strain_form(current_state: dict) -> FormGenerator:
    class StrainForm(FormPage):
        class Config:
            title = "Nieuwe kruising toevoegen"

        strain_name: str
        _validate_strain_name: classmethod = validator("strain_name", allow_reuse=True)(validate_strain_name)

    user_input = yield StrainForm
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

        product_name: str
        product_type: ProductType
        strain_choice: conlist(StrainChoice, min_items=1, max_items=3)
        gebruiken: bool = True
        _validate_product_name: classmethod = validator("product_name", allow_reuse=True)(validate_product_name)

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
