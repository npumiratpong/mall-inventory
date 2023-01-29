from typing import Union, Optional, List, Dict
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from .models import models, schemas
from .service import database_connection
from .service.database import SessionLocal, engine
from .service.controller import authenticate_user, create_access_token, get_current_active_user, get_db

from .api.v1 import auth

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

app.include_router(auth.router, tags=['auth'], prefix='/api/v1')
# app.include_router(user.router, tags=['Users'], prefix='/api/users')

@app.get("/users/me", response_model= schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/{username}", response_model=schemas.User)
def get_user_in_db(username: str = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_user = database_connection.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/me/items/")
async def read_own_items(current_user: models.User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]

@app.get("/healthcheck")
async def read_own_items(current_user: models.User = Depends(get_current_active_user)):
    return [{"Status": "Hello World! "}]