from typing import Optional

from pydantic import BaseModel


class Price(BaseModel):
    price_id: str
    minimal: Optional[int] = None
    amount: Optional[int] = None
    base: float = None
    price: float = None
    name: str
    joint: Optional[bool] = None
    one: Optional[bool] = None
    two: Optional[bool] = None
    five: Optional[bool] = None
    joint: Optional[bool] = None
    product_name: Optional[str] = None
    product_id: Optional[str] = None


class Product(BaseModel):
    product_id: str
    name: str
    amount: float
