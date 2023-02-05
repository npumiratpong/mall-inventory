from typing import Optional, List, Dict

import requests
import json
import datetime
import math

def get_api_response(url, headers={"GUID": "smix", "configFileName": "SMLConfigData.xml", "databaseName": "data1", "provider": "data"}, max_retry:int=3) -> Dict:
    response = requests.get(url=url, headers=headers)
    if response.status_code == 200: body_text = json.loads(response.text)
    # print (response.status_code)
    return body_text, response.status_code

def transform_list2str(items, indexs, index) -> str:
    _items:list = items.get(indexs, None)
    item = [_item[index] for _item in _items] if _items else None
    if item: return str(item).strip("[\'\']").replace("\', '", ", ")
    return None

def get_properties_product(unit_code:str, name_2:str) -> Dict:
    return {
        'name_2': name_2,
        'width_length_height' :unit_code['width_length_height'],
        'weight': unit_code['width_length_height']
    }

def get_barcode_unit(barcode) -> Dict:
    return {
        'barcode': barcode['barcode'] if barcode else None, 
        'barcode_unit': barcode['unit_code'] if barcode else None
    }

# def get_price(barcode_unit:str, price_list:List):
#     price_dict = {
#         "price": 0,
#         "unit_code": barcode_unit
#     }
#     for price in price_list:
#         if price['unit_code'] == barcode_unit:
#             try:
#                 price_dict['price'] = price['price_1'] if float(price['price_1']) != 0 else price['price_2']
#                 price_dict['unit_code'] = barcode_unit
#             except (ValueError) as ev:
#                 print (f"Value Error : {ev} and price_1 {price['price_1']}")
#             return price_dict

def get_product_info(product_id: int, user:Dict) -> Dict:
    url = f"http://27.254.66.181:8080/SMLJavaRESTService/v3/api/product/{product_id}"
    response, status_code = get_api_response(url)
    data = response.get("data", None)
    records = []
    if data:
        barcodes = data.get('barcodes', None)
        unit_standard = data.get('unit_standard', None)
        for unit in data['units']:
            if not barcodes and unit_standard != unit['unit_code']: 
                continue
            re_construct = {}
            re_construct['product_id'] = data.get('code', None)
            re_construct['image_guid'] = transform_list2str(data, "images", "imageGuid")
            re_construct['name'] = data.get('name', None)
            if barcodes:
                for barcode in barcodes:
                    if barcode['unit_code'] == unit['unit_code']:
                        re_construct['barcode'] = get_barcode_unit(barcode)
                        re_construct['properties'] = get_properties_product(unit, data.get('name_2'))
                        break
                    else:
                        re_construct['barcode'] = get_barcode_unit(None)
            elif unit['unit_code'] == unit_standard:
                    re_construct['barcode'] = get_barcode_unit(None)
                    re_construct['properties'] = get_properties_product(unit, data.get('name_2'))
            else:
                break
            re_construct['unit_standard'] = unit_standard
            re_construct['balance_qty'] = data.get('balance_qty', None)
            re_construct['book_out_qty'] = data.get('book_out_qty', None)
            re_construct['accrued_out_qty'] = data.get('accrued_out_qty', None)
            re_construct['item_type'] = data.get('item_type', None)
            re_construct['discount'] = 0
            # re_construct['total_price'] = float(re_construct['price_info']['price']) - float(re_construct['discount'])
            if re_construct['barcode']['barcode_unit'] == unit['unit_code'] or unit['unit_code'] == unit_standard:
                records.append(re_construct)

        print (f"This is records => {records}")

    elif data is None and status_code == 200:
        print (f"Product information of product id {product_id} is not found")
    else:
        print (f"Nothing in Data from response API {data}")
    return records

def get_image_url(image_guid:str) -> None:
    url = f"http://27.254.66.181:8080/SMLJavaRESTService/v3/api/product/image/{image_guid}"
    response, status_code = get_api_response(url)
    return response
