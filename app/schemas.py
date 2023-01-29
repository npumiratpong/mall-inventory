from typing import Union
from pydantic import BaseModel
from datetime import datetime

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

class User(UserBase):
    user_id: int
    username: str
    role: Union[str, None] = None
    is_active: Union[bool, None] = None  

    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class TokenData(BaseModel):
    username: Union[str, None] = None