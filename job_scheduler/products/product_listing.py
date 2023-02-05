import sys
sys.path.append("..") # Adds higher directory to python modules path.

from services.database_connection import insert_product, delete_product

import requests
import json
import datetime
import math

def transform_list2str(items, indexs, index):
    _items:list = items.get(indexs, None)
    item = [_item[index] for _item in _items] if _items else None
    if item: return str(item).strip("[\'\']").replace("\', '", ", ")
    return None

def get_product_from_product_lists(max_retry:int=3) -> None:
    url = "http://27.254.66.181:8080/SMLJavaRESTService/v3/api/product"
    query_param =f"page=1&size=1"
    headers = {"GUID": "smix", "configFileName": "SMLConfigData.xml", "databaseName": "data1", "provider": "data"}
    try:
        reponse = requests.get(url=f"{url}?{query_param}", headers=headers)
        if reponse.status_code == 200:
            body_text = json.loads(reponse.text)
            total = body_text['pages'].get("total_record", None)
            if total:
                size = 1000
                round = math.ceil(total / size) + 1
                created_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for page in range(1, round, 1):
                    query_param = f"page={page}&size={size}"
                    product_response = requests.get(url=f"{url}?{query_param}", headers=headers)
                    products_list = []
                    if product_response.status_code == 200:
                        product_pages = json.loads(product_response.text)
                        for x in product_pages['data']:
                            product = {}
                            product['product_id'] = x.get('code', None)
                            product['product_name'] = x.get('name', None)
                            product['barcode'] = transform_list2str(x, "barcodes", "barcode")
                            product['created_when'] = created_time
                            products_list.append(product)
                        row_affected = insert_product(products_list)
                        print (f"Number of row_affected : {row_affected} rows")
                    elif 400 <= reponse.status_code < 500:
                        print (f"Error occured when calling API endpoint {url} with body {reponse.text}")
                    else:
                        print (f"Connection Error {reponse.text}")
                del_row_affected = delete_product(created_time)
                print (f"Amount of item: {del_row_affected} which older that {created_time} have been removed from database")
                    
        elif 400 <= reponse.status_code < 500:
            print (f"Error occured when calling API endpoint {url} with body {reponse.text}")
        else:
            print (f"Connection Error {reponse.text}")
    except Exception as e:
            print (f"Error occured due to: {e}")

                    
                    



