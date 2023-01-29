from typing import Union, Optional, List, Dict
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status, Request, Response
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi_jwt_auth import AuthJWT
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

from . import crud, models, schemas
from .database import SessionLocal, engine
from .controller import authenticate_user, create_access_token, get_current_active_user, get_db, \
    ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES, oauth2_scheme, SECRET_KEY, ALGORITHM, validate_refresh_token

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

@app.post("/login", response_model= schemas.Token)
async def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    if not form_data.username or not form_data.password:
        raise HTTPException(status_code=401, detail="Username and Password are required")
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=401, 
            detail= "Incorrect Username or Password",
            headers= {"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive User")
    access_token = create_access_token(data = {"User": user.username, "Role": user.role}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    refresh_token = create_access_token(data = {"User": user.username, "Role": user.role}, expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES))

    response.set_cookie('access_token', access_token)
    response.set_cookie('refresh_token', refresh_token)
    response.set_cookie('token_type', "Bearer")

    return {"access_token": access_token,"refresh_token": refresh_token , "token_type": "Bearer"}

@app.post('/refresh')
def refresh(response: Response, current_user: schemas.User = Depends(get_current_active_user), response_model= schemas.RefreshToken):
    if not current_user.username:
        raise HTTPException(status_code=401, detail="Unauthorized")
    access_token = create_access_token(data = {"User": current_user.username, "Role": current_user.role}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie('access_token', access_token)
    return {"access_token": access_token, "token_type": "Bearer"}
    

@app.get('/logout', response_model= schemas.Logout)
def logout(response: Response, current_user: schemas.User = Depends(get_current_active_user)):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("token_type")
    return {"status": "success"}

@app.get("/users/me", response_model= schemas.User)
async def read_users_me(current_user: schemas.User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/{username}", response_model=schemas.User)
def get_user_in_db(username: str = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@app.get("/users/me/items/")
async def read_own_items(current_user: models.User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]