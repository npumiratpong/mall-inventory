import requests
import json


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
                size = 100
                round = total // size
                print (round)
                for page in range(1, round, 1):
                    query_param = f"page={page}&size={size}"
                    product_response = requests.get(url=f"{url}?{query_param}", headers=headers)
                    if product_response.status_code == 200:
                        product_list = json.loads(product_response.text)
        elif 400 <= reponse.status_code < 500:
            print (f"Error occured when calling API endpoint {url} with body {reponse.text}")
        else:
            print (f"Connection Error {reponse.text}")
    except Exception as e:
            print (f"Error occured due to: {e}")

                    
                    



