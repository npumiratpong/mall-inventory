from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from fastapi import Request
from typing import Dict, List, Optional, Union

from ..models import models
from ..models import schemas


def create_user_item(db: Session, item: schemas.ItemCreate, user_id: int):
    db_item = models.Item(**item.dict(), owner_id=user_id)
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


def get_user_by_username(db: Session, username: str) -> Dict:
    sql = text(f"SELECT u.user_id, u.username, u.hashed_password,r.role_name, u.is_active FROM users u " \
               f"INNER JOIN user_mapping um " \
               f"ON u.user_id = um.user_id " \
               f"INNER JOIN roles r " \
               f"ON r.role_id = um.role_id "\
               f"WHERE u.username = '{username}'")
    result = db.execute(sql).fetchall()[0]
    user = {
        "user_id": result[0],
        "username": result[1],
        "hashed_password": result[2],
        "role": result[3],
        "is_active": result[4]
    }
    return schemas.User(**user)


def get_items(db: Session, type: str) -> List:
    sql = text(f"SELECT {type} FROM Products")
    result = db.execute(sql).fetchall()
    if result:
        if len(result) == 1:
            items = str(result[0]).strip("()',")
        else:
            items: list = [str(x).strip("()',") for x in result]
    return items
