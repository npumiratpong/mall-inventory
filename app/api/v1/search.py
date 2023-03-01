from fastapi import Depends, APIRouter, Query, HTTPException

from typing import Dict, List
from pydantic import parse_obj_as

from api.v1.get_item_properties import get_product_info
from service.controller import get_db,  get_current_active_user
from service.database_connection import get_all_items, get_product_by_search_term
from models.schemas import User, ProductModel

router = APIRouter()

@router.get('', response_model=ProductModel)
def search_product(search_term:str = Query(default=None), limit:int = Query(default=20), 
                   customer_name:str = Query(default=None), current_user: User = Depends(get_current_active_user)):
    response = None
    response_bulk = []
    products = {}
    if search_term:
        ids = get_product_by_search_term(limit, search_term)
        if ids:
            for id in ids:
                responses = get_product_info(product_id=id,
                                            user=current_user,
                                            cust_name=customer_name)
                
                if isinstance(responses, list):
                    for response in responses:
                        response_bulk.append(response)
                else:
                    continue
    if len(response_bulk) == 0:
        raise HTTPException(status_code=404, detail="Item not found")
    products['products'] = response_bulk
    return products

@router.get('/pre-search/{type}')
def get_product_from_product_lists(type:str, current_user: User = Depends(get_current_active_user)) -> Dict:
    items = None
    items = get_all_items(type=type)
    return {"fetch_items": items}
