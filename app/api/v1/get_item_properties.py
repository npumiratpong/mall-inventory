from typing import Optional, List, Dict, Any
from models.schemas import User
from service.database_connection import get_product_price_for_mall, get_discount_price
from requests.adapters import HTTPAdapter, Retry
from fastapi import HTTPException


import requests
import json
import yaml
import os

env = os.environ['TYPE_ENV']

config_path = 'api/v1/product_api.yml'

with open(config_path, 'r') as file:
    doc = yaml.load(file, Loader=yaml.FullLoader)

config = doc[env]

def get_api_response(url, headers, params={}, timeout:int=5) -> Dict:
    body_text = ''
    retry_strategy = Retry(
                            total=3,
                            backoff_factor=1,
                            status_forcelist=[429, 500, 502, 503, 504]
                            )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.HTTPError as errh:
        print("SML HTTP Error:", errh)
        raise HTTPException(status_code=502, detail=f"SML HTTP Error")
    except requests.exceptions.ConnectionError as errc:
        print("SML Connection Error:", errc)
        raise HTTPException(status_code=503, detail=f"SML Connection Error")
    except requests.exceptions.Timeout as errt:
        print("SML Timeout Error:", errt)
        raise HTTPException(status_code=504, detail=f"SML Timeout Error")
    except requests.exceptions.RequestException as err:
        print("Something went wrong with SML:", err)
        raise HTTPException(status_code=500, detail=f"Something went wrong with SML")
    else:
        if response.status_code == 200: body_text = json.loads(response.text)
    return body_text, response.status_code

def transform_list2str(items, indexs, index) -> str:
    _items:list = items.get(indexs, None)
    item = [_item[index] for _item in _items] if _items else None
    if item: return str(item).strip("[\'\']").replace("\', '", ", ")
    return None

def get_properties_product(weight:str, width:str, name_2:str) -> str:
    prop = ''
    if name_2:
        prop += name_2
    if weight:
        prop += ' ' + weight
    if width:
        prop += ' ' + width
    return prop if prop else None

def get_barcode_unit(barcode:str, barcode_unit:str) -> Dict:
    bar = ''
    if barcode:
        bar += barcode
    if barcode_unit:
        bar += ' (' + barcode_unit + ')'
    return bar if bar else None

def get_standard_value(units:List):
    for unit in units:
        if unit.get('unit_code') == 'ลัง':
            return unit.get('stand_value')
    return None

def get_price(price:str, price_unit:str) -> str:
    pric = ''

    if price:
        pric += str("{:.2f}".format(float(price)))
    if price_unit:
        pric += ' / ' + price_unit

    if pric == '0.00 / N/A': pric = ''

    return pric, float(price)

def determine_discount_price(code:str, barcode:str, unit_standard:str, user_role:str, customer_name:str):
    discount = 0
    if user_role in ['admin', 'sale_store', 'sale_admin_store'] and customer_name == 'store_price':
        if barcode is not None:
            barcode = barcode.split()[-1].strip('()')
        unit = barcode if barcode else unit_standard
        discount = float(get_discount_price(code, unit))
    discount_number = (100 - discount)/100
    if int(discount) == 0:
        return '', 1
    return "{} (%)".format(int(discount)), discount_number

def determine_price_by_store(price_formulas:List, user_role:str) -> Any:
    price = {}
    if user_role not in ['admin', 'sale_store', 'sale_admin_store'] or not price_formulas:
        return None, None
    else:
        if price_formulas:
            for price_dict in price_formulas:
                if price_dict.get("unit_code") == "โหล":
                    price = price_dict.get("price_1")
                    if price and price != 0:
                        return price, price_dict.get("unit_code")
            for price_dict in price_formulas:
                if price_dict.get("unit_code") == "ชิ้น":
                    price = price_dict.get("price_2")
                    if price and price != 0:
                        return price, price_dict.get("unit_code")
                    price = price_dict.get("price_0")
                    if price and price != 0:
                        return price, price_dict.get("unit_code")
            for price_dict in price_formulas:
                if price_dict.get("unit_code") == "แพ็ค":
                    price = price_dict.get("price_3")
                    if price and price != 0:
                        return price, price_dict.get("unit_code")
            return None, None
        
def determin_price_by_mall(product_id:str, barcode_unit:str, customer_name:str) -> str:
    if '(' in barcode_unit or ')' in barcode_unit:
        barcode_unit = barcode_unit.split()[-1].strip('()')
    price = get_product_price_for_mall(product_id, barcode_unit, customer_name)[0]
    if price:
        return price, barcode_unit
    else:
        return None, barcode_unit

def finalize_price(price_formulas:List, code:str, barcode:str, unit_standard:str, user_role:str, customer_name:str):
    default_price = '0.00'
    default_unitcode = 'N/A'
    user_type = 'Store' if customer_name == 'store_price' else 'Mall'
    if customer_name == 'store_price':
        final_price, final_code = determine_price_by_store(price_formulas, user_role)
    else:
        final_price, final_code = determin_price_by_mall(code, barcode if barcode else unit_standard, customer_name)

    price_form, price = get_price(final_price if final_price else default_price, 
                                  final_code if final_code else default_unitcode)
                                  
    print (f"::: Price: {price_form} from Determine Price By {user_type} of prouct ID: {code} by customer : {customer_name}:::")
    if price_form.startswith('0.00'):
        return '', None
    return price_form, price
    
def record_mapping(pre_record:Dict, barcode:str, price_formulas:List, user_role:str, customer_name:str) -> Dict:
    re_construct = {}
    re_construct['images'] = pre_record.get('images', None)
    re_construct['barcode'] = barcode
    re_construct['code'] = pre_record.get('code', None)
    re_construct['name'] = pre_record.get('name', None)
    re_construct['properties'] = pre_record.get('properties', None)
    re_construct['unit_standard'] = pre_record.get('unit_standard', None)
    re_construct['book_out_qty'] = pre_record.get('book_out_qty', 0)
    re_construct['accrued_out_qty'] = pre_record.get('accrued_out_qty', 0)
    re_construct['balance_qty_net'] = pre_record.get('balance_qty', 0) - re_construct['book_out_qty'] - re_construct['accrued_out_qty'] 
    re_construct['item_type'] = pre_record.get('item_type', None)
    re_construct['stand_value'] = pre_record.get('stand_value', None)
    re_construct['discount'], discount_formula = determine_discount_price(re_construct['code'], re_construct['barcode'], re_construct['unit_standard'], user_role, customer_name)
    re_construct['price'], price_formula = finalize_price(price_formulas, re_construct['code'], re_construct['barcode'], re_construct['unit_standard'],
                                                          user_role, customer_name)
    re_construct['total_price'] = str("{:.2f}".format(float(price_formula * discount_formula))) if price_formula else ''
    return re_construct         

def get_product_info(product_id: int, user:Dict, cust_name:str) -> Dict:
    user_role = user.role
    customer_name = cust_name
    pre_record = {}
    
    url = f"{config['url']}/{product_id}"
    response, status_code = get_api_response(url,
                                            headers={"GUID": config["GUID"], 
                                                     "configFileName": config["configFileName"], 
                                                     "databaseName": config["databaseName"], 
                                                     "provider": config["provider"]})
    data = response.get("data", None)
    weight = None
    width = None
    record = {}
    records = []
    if data:
        weight = data['units'][0].get('width_length_height', None)
        width = data['units'][0].get('weight', None)
        name_2 = data.get('name_2', None)
        properties = get_properties_product(weight, width, name_2)
        barcodes = data.get('barcodes', None)
        pre_record['code'] = data.get('code', None)
        pre_record['name'] = data.get('name', None)
        pre_record['images'] = transform_list2str(data, "images", "imageGuid")
        pre_record['balance_qty'] = data.get('balance_qty', None)
        pre_record['book_out_qty'] = data.get('book_out_qty', None)
        pre_record['accrued_out_qty'] = data.get('accrued_out_qty', None)
        pre_record['price_formulas'] = data.get('price_formulas', None)
        pre_record['unit_standard'] = data.get('unit_standard', None)
        pre_record['item_type'] = data.get('item_type', None)
        pre_record['properties'] = properties
        pre_record['stand_value'] = get_standard_value(data['units'])

        if barcodes:
            for barcode in barcodes:
                for unit in data['units']:
                    if barcode['unit_code'] is None or len(barcode['unit_code']) == 0:
                        barcode_data = get_barcode_unit(barcode['barcode'], barcode['unit_code'])
                        record = record_mapping(pre_record, barcode_data, pre_record['price_formulas'], user_role, customer_name)
                        break                        
                    elif barcode['unit_code'] == unit['unit_code']:
                        barcode_data = get_barcode_unit(barcode['barcode'], barcode['unit_code'])
                        record = record_mapping(pre_record, barcode_data, pre_record['price_formulas'], user_role, customer_name)
                        break
                if record: 
                    records.append(record) 
        else:
            for unit in data['units']:
                if unit['unit_code'] == pre_record['unit_standard']:
                    record = record_mapping(pre_record, None, pre_record['price_formulas'], user_role, customer_name)
                    records.append(record)
                    break

    elif data is None and status_code == 200:
        print (f"Product information of product id {product_id} is not found")
    else:
        print (f"Nothing in Data from response API {data}")
    return records

def get_image_url(image_guid:str) -> None:
    url = f"{config['url']}/image/{image_guid}"
    response, status_code = get_api_response(url)
    return response
