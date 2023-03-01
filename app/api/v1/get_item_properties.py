from typing import Optional, List, Dict
from models.schemas import User
from service.database_connection import get_product_price_for_mall
import requests
import json

def get_api_response(url, headers={"GUID": "smix", "configFileName": "SMLConfigData.xml", "databaseName": "data1", "provider": "data"}, max_retry:int=3) -> Dict:
    response = requests.get(url=url, headers=headers, timeout=10)
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

def get_price(price:str, price_unit:str) -> str:
    pric = ''
    if price:
        pric += str(round(float(price), 3))
    if price_unit:
        pric += ' / ' + price_unit
    return pric if pric else 0

def determine_price_by_store(price_formulas:List) -> Dict:
    print (f"::: Determine Price By Store :::")
    price = {}
    if not price_formulas and user_role not in ['sale_store', 'sale_admin_store']:
        return 0, None
    if user_role in ['sale_store', 'sale_admin_store']:
        return None, None
    else:
        if price_formulas:
            for price_dict in price_formulas:
                if price_dict.get("unit_code") == "โหล":
                    price = price_dict.get("price_1")
                    if price:
                        return price, price_dict.get("unit_code")
            for price_dict in price_formulas:
                if price_dict.get("unit_code") == "ชิ้น":
                    price = price_dict.get("price_2")
                    if price:
                        return price, price_dict.get("unit_code")
                    price = price_dict.get("price_0")
                    if price:
                        return price, price_dict.get("unit_code")
            for price_dict in price_formulas:
                if price_dict.get("unit_code") == "แพ็ค":
                    price = price_dict.get("price_3")
                    if price:
                        return price, price_dict.get("unit_code")
            return 0, None
        
def determin_price_by_mall(product_id:str, barcode_unit:str):
    print (f"::: Determine Price By Mall :::")
    if '(' in barcode_unit or ')' in barcode_unit:
        barcode_unit = barcode_unit.split()[-1].strip('()')
    price = get_product_price_for_mall(product_id, barcode_unit, customer_name)[0]
    if price:
        return get_price(price, barcode_unit)
    return 0

def record_mapping(pre_record:Dict, barcode:str, price_formulas:List=None) -> Dict:
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
    re_construct['discount'] = 0
    re_construct['price'] = get_price(*determine_price_by_store(price_formulas)) if price_formulas and user_role not in ['sale_shopping_mall','sale_admin_shopping_mall'] \
                                                                                    or customer_name == 'store_price' \
                                                                                 else determin_price_by_mall(re_construct['code'],
                                                                                      barcode if barcode else re_construct['unit_standard'])
    re_construct['total_price'] = round(float(str(re_construct['price']).split()[0]) - float(re_construct['discount']), 2)
    return re_construct         

def get_product_info(product_id: int, user:Dict, cust_name:str) -> Dict:
    global user_role
    global customer_name
    user_role = user.role
    customer_name = cust_name
    pre_record = {}
    
    url = f"http://27.254.66.181:8080/SMLJavaRESTService/v3/api/product/{product_id}"
    response, status_code = get_api_response(url)
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

        if barcodes:
            for barcode in barcodes:
                for unit in data['units']:
                    if barcode['unit_code'] is None or len(barcode['unit_code']) == 0:
                        barcode_data = get_barcode_unit(barcode['barcode'], barcode['unit_code'])
                        record = record_mapping(pre_record, barcode_data, pre_record['price_formulas'])
                        break                        
                    elif barcode['unit_code'] == unit['unit_code']:
                        barcode_data = get_barcode_unit(barcode['barcode'], barcode['unit_code'])
                        record = record_mapping(pre_record, barcode_data, pre_record['price_formulas'])
                        break
                if record: 
                    records.append(record) 
        else:
            for unit in data['units']:
                if unit['unit_code'] == pre_record['unit_standard']:
                    record = record_mapping(pre_record, None, pre_record['price_formulas'])
                    records.append(record)
                    break

    elif data is None and status_code == 200:
        print (f"Product information of product id {product_id} is not found")
    else:
        print (f"Nothing in Data from response API {data}")
    return records

def get_image_url(image_guid:str) -> None:
    url = f"http://27.254.66.181:8080/SMLJavaRESTService/v3/api/product/image/{image_guid}"
    response, status_code = get_api_response(url)
    return response
