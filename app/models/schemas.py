from typing import Union, Optional, List, Dict
from pydantic import BaseModel
from datetime import datetime
from pydantic import BaseModel, Field
from decimal import Decimal

class ItemBase(BaseModel):
    title: str
    description: Union[str, None] = None

class ItemCreate(ItemBase):
    pass

class Item(ItemBase):
    id: int
    owner_id: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    email: Union[str, None] = None
    modified_when: Union[datetime, None] = None
    created_when: Union[datetime, None] = None

class UserCreate(UserBase):
    password: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class RefreshToken(BaseModel):
    access_token: str
    token_type: str

class Logout(BaseModel):
    status: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    user_id: int
    username: str
    hashed_password: str
    role: Optional[str] = None
    is_active: Optional[bool] = None  

class Search(BaseModel):
    product_id: List[str]

class PreSearch(BaseModel):
    items: List[str]

class ProductBaseModel(BaseModel):
    images: Optional[str]
    barcode: Optional[str]
    code: Optional[str]
    name: Optional[str]
    properties: Optional[str]
    unit_standard: Optional[str]
    balance_qty: Optional[int] = 0
    book_out_qty: Optional[int] = 0
    accrued_out_qty: Optional[int] = 0
    item_type: Optional[int]
    discount: float = 0
    price: str = 0
    total_price: float = 0

ProductList = List[ProductBaseModel]

class ProductModel(BaseModel):
    products: ProductList
