from service import database, database_connection
from service.database_connection import insert_product
import sys
import requests
import json
import sys
import datetime
import math

def get_product_from_product_lists() -> None:
    url = "http://27.254.66.181:8080/SMLJavaRESTService/v3/api/product"
    query_param =f"page=1&size=1"
    headers = {"GUID": "smix", "configFileName": "SMLConfigData.xml", "databaseName": "test", "provider": "data"}
    try:
        reponse = requests.get(url=f"{url}?{query_param}", headers=headers)
        if reponse.status_code == 200:
            body_text = json.loads(reponse.text)
            total = body_text['pages'].get("total_record", None)
            if total:
                size = 1000
                round = math.ceil(total / size)
                created_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for page in range(1, round+1, 1):
                    query_param = f"page={page}&size={size}"
                    product_response = requests.get(url=f"{url}?{query_param}", headers=headers)
                    products_list = []
                    if product_response.status_code == 200:
                        product_pages = json.loads(product_response.text)
                        for x in product_pages['data']:
                            product = {}
                            _barcodes = x.get('barcodes', None)
                            barcodes = [barcode['barcode'] for barcode in _barcodes] if _barcodes else None
                            product['product_id'] = x.get('code', None)
                            product['product_name'] = x.get('name', None)
                            product['barcode'] = str(barcodes).strip("[\'\']").replace("\', '", ", ")
                            product['created_when'] = created_time
                            products_list.append(product)
                    insert_product(products_list)
        elif 400 <= reponse.status_code < 500:
            print (f"Error occured when calling API endpoint {url} with body {reponse.text}")
        else:
            print (f"Connection Error {reponse.text}")
    except Exception as e:
            print (f"Error occured due to: {e}")

                    
                    



