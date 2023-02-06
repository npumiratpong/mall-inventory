from fastapi import Depends, APIRouter, Response, HTTPException
from sqlalchemy.orm import Session

from typing import Dict, List
from pydantic import parse_obj_as

from api.v1.get_item_properties import get_product_info
from service.controller import get_db,  get_current_active_user
from service.database_connection import get_all_items, get_product_by_search_term
from models.schemas import ProductResponse, User

router = APIRouter()

@router.get('', response_model=ProductResponse)
def search_product(search_term:str = None, limit:int = 20, current_user: User = Depends(get_current_active_user)):
    response = None
    response_bulk = []
    if search_term:
        search_term = search_term.strip()
        ids = get_product_by_search_term(limit, search_term)
        if ids:
            for id in ids:
                responses = get_product_info(product_id=id,
                                            user=current_user)
                if isinstance(responses, list):
                    for response in responses:
                        response_bulk.append(response)
                else:
                    continue
    print (type(response_bulk))
    return {'products': response_bulk}

@router.get('/pre-search/{type}')
def get_product_from_product_lists(type:str, current_user: User = Depends(get_current_active_user)) -> Dict:
    items = None
    items = get_all_items(type=type)
    return {"fetch_items": items}
