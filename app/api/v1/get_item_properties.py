from typing import Optional, List, Dict

import requests
import json
import datetime
import math

def get_api_response(url, headers={"GUID": "smix", "configFileName": "SMLConfigData.xml", "databaseName": "data1", "provider": "data"}, max_retry:int=3) -> Dict:
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200: body_text = json.loads(response.text)
    return body_text

def transform_list2str(items, indexs, index) -> str:
    _items:list = items.get(indexs, None)
    item = [_item[index] for _item in _items] if _items else None
    if item: return str(item).strip("[\'\']").replace("\', '", ", ")
    return None

def properties_product(unit_code:str, name_2:str, unit_standard:str =None, barcodes:List[Dict] =None) -> Dict:
    properties = {}
    properties['name_2'] = name_2
    if barcodes:
        for barcode in barcodes:
            if barcode['unit_code'] == unit_code['unit_code']:
                properties['width_length_height'] = unit_code['width_length_height']
                properties['weight'] = unit_code['weight']
            else:
                properties['width_length_height'] = unit_code['width_length_height']
                properties['weight'] = unit_code['weight']
    else:
        properties['width_length_height'] = unit_code['width_length_height']
        properties['weight'] = unit_code['weight']   
    return properties


def get_price(barcode_unit:str, price_list:List):
    price_dict = {
        "price": 0,
        "unit_code": barcode_unit
    }
    for price in price_list:
        if price['unit_code'] == barcode_unit:
            try:
                price_dict['price'] = price['price_1'] if float(price['price_1']) != 0 else price['price_2']
                price_dict['unit_code'] = barcode_unit
            except (ValueError) as ev:
                print (f"Value Error : {ev} and price_1 {price['price_1']}")
            return price_dict

def get_product_info(product_id: int, user:Dict) -> Dict:
    url = f"http://27.254.66.181:8080/SMLJavaRESTService/v3/api/product/{product_id}"
    response = get_api_response(url)
    data = response.get("data", None)
    if data:
        barcodes = data.get('barcodes', None)
        unit_standard = data.get('unit_standard', None)
        records = []
        for unit in data['units']:
            re_construct = {}
            if not barcodes and unit_standard != unit['unit_code']: 
                continue
            try:
                if barcodes:
                    for barcode in barcodes:
                        if barcode['unit_code'] == unit['unit_code']:
                            re_construct['price_info'] = get_price(barcode['unit_code'], data['price_formulas']) if user.role not in ['sale_shopping_mall', 'sale_admin_shopping_mall'] \
                                                                                                            and data['price_formulas'] \
                                                                                                            else 0
                            re_construct['properties'] = properties_product(unit, data.get('name_2', None), unit_standard, barcodes)
                        else:
                            continue
                else:
                    re_construct['properties'] = properties_product(unit, data.get('name_2', None), unit_standard)
            except Exception as e:
                print (f"An error occurred due to : {e}")
            finally:
                re_construct['unit_standard'] = data.get('unit_standard', None)
                re_construct['product_id'] = data.get('code', None)
                re_construct['image_guid'] = transform_list2str(data, "images", "imageGuid")
                re_construct['name'] = data.get('name', None)
                re_construct['balance_qty'] = data.get('balance_qty', None)
                re_construct['book_out_qty'] = data.get('book_out_qty', None)
                re_construct['accrued_out_qty'] = data.get('accrued_out_qty', None)
                re_construct['item_type'] = data.get('item_type', None)
                re_construct['discount'] = 0
                re_construct['total_price'] = float(re_construct['price_info']['price']) - float(re_construct['discount'])
                if barcode['unit_code'] == unit['unit_code']:
                    records.append(re_construct)

    print (f"This is records => {len(records)}")
    print (f"This is records => {records}")

    return response

def get_image_url(image_guid:str) -> None:
    url = f"http://27.254.66.181:8080/SMLJavaRESTService/v3/api/product/image/{image_guid}"
    response = get_api_response(url)
    return response
