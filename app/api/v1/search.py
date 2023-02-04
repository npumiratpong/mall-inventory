from fastapi import Depends, APIRouter, Response, HTTPException
from sqlalchemy.orm import Session

from typing import Dict, List

from ...service.controller import get_db,  get_current_active_user
from ...service.database_connection import get_items
from ...models import schemas

router = APIRouter()

@router.get('/pre-search/{type}')
def get_product_from_product_lists(type:str, current_user: schemas.User = Depends(get_current_active_user)) -> Dict:
    items = get_items(type=type)
    return {"fetch_items": items}