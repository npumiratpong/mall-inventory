from typing import Union, Optional, List
from sqlalchemy import Column, Integer, String
from datetime import datetime

from ..service.database import Base


class product(Base):
    __tablename__ = "products"
    product_id = Column(String(50), primary_key=True)
    product_name = Column(String(255))
    barcodes = Column(String(1000))
    created_when = Column(datetime)

