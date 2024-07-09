from typing import Optional

from pydantic import BaseModel


class Weight(BaseModel):
    product_id: int
    weight: float

class Price(BaseModel):
    price_id: str
    category: str
    name: str
    minimal: Optional[int] = None
    amount: Optional[int] = None
    base: float = None
    price: float = None
    joint: Optional[bool] = None
    one: Optional[bool] = None
    two: Optional[bool] = None
    five: Optional[bool] = None
    joint: Optional[bool] = None
    product_name: Optional[str] = None
    product_id: Optional[int] = None
    weight: list[Weight]



class Product(BaseModel):
    product_id: int
    name: str
    amount: float
