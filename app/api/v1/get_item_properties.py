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

def get_price(price:str, price_unit:str) -> Dict:
    pric = ''
    if price:
        pric += price
    if price_unit:
        pric += ' / ' + price_unit
    return pric if pric else None

def determine_price(units:List, price_formulas:List, role:str) -> Dict:
    price = {}
    print (f"Hello you are in determine price with role {role}")
    if not price_formulas and role not in ['sale_store', 'sale_admin_store']:
        return 0
    if role in ['sale_store', 'sale_admin_store']:
        pass
    else:
        if price_formulas:
            print (f"Hello you are in determine price with role {role} in last else")
            count = 0
            while True:
                if str(price_formulas[count]['unit_code']).strip().startswith("โหล") or price_formulas[count]['unit_code'] == 'โหล':
                    price['from_unit'] = price_formulas[count]['unit_code']
                    if price_formulas[count]['price_1'] is not None and len(price_formulas[count]['price_1']) > 0:
                        print (f"Hello you are in determine price with role {role} in last else in first if")
                        price['price'] = price_formulas[count]['price_1']
                elif str(price_formulas[count]['unit_code']).strip().startswith("ชิ้น") or price_formulas[count]['unit_code'] == 'ชิ้น':
                    price['from_unit'] = price_formulas[count]['unit_code']
                    print (f"Hello you are in determine price with role {role} in last else in elif 2")
                    if price_formulas[count]['price_2'] is not None and len(price_formulas[count]['price_2']) > 0:
                        print (f"Hello you are in determine price with role {role} in last else in elif 2 first if")
                        price['price'] = price_formulas[count]['price_2']
                    elif price_formulas[count]['price_0'] is not None and len(price_formulas[count]['price_0']) > 0:
                        print (f"Hello you are in determine price with role {role} in last else in elif 2 elif 1")
                        price['price'] = price_formulas[count]['price_0']
                    elif price_formulas[count]['price_1'] is not None and len(price_formulas[count]['price_1']) > 0:
                        price['price'] = price_formulas[count]['price_1']
                elif str(price_formulas[count]['unit_code']).strip().startswith("แพ็ค") or price_formulas[count]['unit_code'] == 'แพ็ค':
                    price['from_unit'] = price_formulas[count]['unit_code']
                    print (f"Hello you are in determine price with role {role} in last else in elif 3")
                    if price_formulas[count]['price_3'] is not None and len(price_formulas[count]['price_3']) > 0:
                        price['price'] = price_formulas[count]['price_3']

                if count == len(price_formulas):
                    price['price'] = 0.00
                if price:
                    print (f"This is FINAL PRICE when going out {price}")
                    return price
                count = count + 1 if count < 3 else 0 

def record_mapping(pre_record:Dict, barcode:str, price:str=None) -> Dict:
    re_construct = {}
    re_construct['product_id'] = pre_record.get('code', None)
    re_construct['image_guid'] = pre_record.get('images', None)
    re_construct['name'] = pre_record.get('name', None)
    re_construct['barcode'] = barcode
    re_construct['properties'] = pre_record.get('properties', None)
    re_construct['unit_standard'] = pre_record.get('unit_standard', None)
    re_construct['balance_qty'] = pre_record.get('balance_qty', None)
    re_construct['book_out_qty'] = pre_record.get('book_out_qty', None)
    re_construct['accrued_out_qty'] = pre_record.get('accrued_out_qty', None)
    re_construct['item_type'] = pre_record.get('item_type', None)
    re_construct['discount'] = 0
    re_construct['price'] = price
    return re_construct         

def get_product_info(product_id: int, user:Dict) -> Dict:
    url = f"http://27.254.66.181:8080/SMLJavaRESTService/v3/api/product/{product_id}"
    response, status_code = get_api_response(url)
    data = response.get("data", None)
    pre_record = {}
    weight = None
    width = None
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

        # print (f"This is pre-re =============>>>  {pre_record}  <=====")
        if barcodes:
            for barcode in barcodes:
                for unit in data['units']:
                    if barcode['unit_code'] is None or len(barcode['unit_code']) == 0:
                        barcode_data = get_barcode_unit(barcode['barcode'], barcode['unit_code'])
                        pre_record['price'] = determine_price(data['units'], pre_record['price_formulas'], user.role)
                        price = get_price(pre_record['price']['price'], pre_record['price']['from_unit'])
                        print (f"This is what price get you {pre_record['price']}")
                        record = record_mapping(pre_record, barcode_data, price)
                        break                        
                    else:
                        if barcode['unit_code'] == unit['unit_code']:
                            barcode_data = get_barcode_unit(barcode['barcode'], barcode['unit_code'])
                            record = record_mapping(pre_record, barcode_data)
                            break
                records.append(record)   
        else:
            for unit in data['units']:
                if unit['unit_code'] == pre_record['unit_standard']:
                    record = record_mapping(pre_record, None)
                    records.append(record)
                    break

    elif data is None and status_code == 200:
        print (f"Product information of product id {product_id} is not found")
    else:
        print (f"Nothing in Data from response API {data}")

    print (f"This is appending record {records}")
    
    return records

def get_image_url(image_guid:str) -> None:
    url = f"http://27.254.66.181:8080/SMLJavaRESTService/v3/api/product/image/{image_guid}"
    response, status_code = get_api_response(url)
    return response
