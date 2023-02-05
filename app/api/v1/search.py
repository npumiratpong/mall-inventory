from fastapi import Depends, APIRouter, Response, HTTPException
from sqlalchemy.orm import Session

from typing import Dict, List
from pydantic import parse_obj_as

from api.v1.get_item_properties import get_product_info
from service.controller import get_db,  get_current_active_user
from service.database_connection import get_all_items, get_product_id
from models.schemas import ProductInformation, User

router = APIRouter()

@router.get('')
def search_product(barcode:str = None, product_name:str = None, product_id:str = None, current_user: User = Depends(get_current_active_user)):
    print (f"This is barcode: {barcode}")
    print (f"This is product_name: {product_name}")
    print (f"This is role: {current_user.role}")
    response = None
    if product_id:
        print (product_id)
        response = get_product_info(product_id=product_id.strip(), 
                                    user=current_user)
    else:
        if barcode is not None: barcode = barcode.strip()
        if product_name is not None: product_name = product_name.strip()
        ids = get_product_id(barcode, product_name)
        if ids:
            for id in ids:
                response = get_product_info(product_id=id,
                                            user=current_user)
                
    return {'products': response}

@router.get('/pre-search/{type}')
def get_product_from_product_lists(type:str, current_user: User = Depends(get_current_active_user)) -> Dict:
    items = None
    items = get_all_items(type=type)
    return {"fetch_items": items}
