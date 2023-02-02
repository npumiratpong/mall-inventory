from sqlalchemy.orm import Session
from typing import Dict, List, Optional, Union

from .database import engine

from ..models import models
from ..models import schemas

def execute_sql_statement(sql_statement, params=None):
    with engine.connect() as conn:
        result = conn.exec_driver_sql(sql_statement, parameters=params).fetchall()
    return result
    

def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_user_by_username(username: str) -> Dict:
    sql =f"SELECT u.user_id, u.username, u.hashed_password,r.role_name, u.is_active FROM users u " \
         f"INNER JOIN user_mapping um " \
         f"ON u.user_id = um.user_id " \
         f"INNER JOIN roles r " \
         f"ON r.role_id = um.role_id " \
         f"WHERE u.username = %(username)s"

    params = {"username": username}
    
    result = execute_sql_statement(sql, params)
    
    if not result: 
        return None
    else:
        user = {"user_id": result[0][0],
                "username": result[0][1],
                "hashed_password": result[0][2],
                "role": result[0][3],
                "is_active": result[0][4]}    
        return schemas.User(**user)

def get_items(type: str) -> List:
    sql = f"SELECT {type} FROM Products"
    result = execute_sql_statement(sql)
    if not result: return []
    else: return [str(x).strip("()',") for x in result]
