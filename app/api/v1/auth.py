from fastapi import Depends, APIRouter, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from ...models import schemas, models
from ...service.controller import authenticate_user, create_access_token, get_db, get_current_active_user

ACCESS_TOKEN_EXPIRE_MINUTES = 60
REFRESH_TOKEN_EXPIRE_MINUTES = 360

router = APIRouter()

@router.post("/login", response_model= schemas.Token)
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

@router.post('/refresh', response_model= schemas.RefreshToken)
def refresh(response: Response, current_user: schemas.User = Depends(get_current_active_user)):
    if not current_user.username:
        raise HTTPException(status_code=401, detail="Unauthorized")
    access_token = create_access_token(data = {"User": current_user.username, "Role": current_user.role}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    response.set_cookie('access_token', access_token)
    return {"access_token": access_token, "token_type": "Bearer"}
    

@router.get('/logout', response_model= schemas.Logout)
def logout(response: Response, current_user: schemas.User = Depends(get_current_active_user)):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("token_type")
    return {"status": "success"}