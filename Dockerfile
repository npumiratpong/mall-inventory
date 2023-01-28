# 
FROM python:3.9

WORKDIR /mall-inventory

COPY ./requirements.txt /mall-inventory/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /mall-inventory/requirements.txt
COPY ./app /mall-inventory/app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "80"]