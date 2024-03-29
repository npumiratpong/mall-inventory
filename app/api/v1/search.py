from fastapi import Depends, APIRouter, Query

from typing import Dict, List
from pydantic import parse_obj_as

from api.v1.get_item_properties import get_product_info
from service.controller import get_db,  get_current_active_user
from service.database_connection import get_all_items, get_product_by_search_term, get_customer_names, count_all_items_by_search_item
from models.schemas import User, ProductModel, CustomerName

router = APIRouter()

@router.get('', response_model=ProductModel)
def search_product(search_term:str = Query(default=None), limit:int = Query(default=1000), 
                   customer_name:str = Query(default=None), current_user: User = Depends(get_current_active_user)):
    response = None
    counts = 0
    response_bulk = []
    products = {}
    if search_term:
        counts = count_all_items_by_search_item(search_term)
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
    products['total_items'] = counts
    products['products'] = response_bulk
    return products

@router.get('/customer_names', response_model=CustomerName)
def get_product_from_product_lists(current_user: User = Depends(get_current_active_user)):
    names = None
    names = get_customer_names()
    return {"customer_names": names}
