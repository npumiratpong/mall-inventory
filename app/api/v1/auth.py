from fastapi import Depends, APIRouter, Response, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from datetime import datetime, timedelta
from models import schemas
from service.controller import authenticate_user, create_access_token, get_db, get_current_active_user,verify_refresh_token

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
def refresh_access_token(response: Response, refresh_token:str):
    # Get refresh data, will return username, role to create new accesss token
    refesh_data = verify_refresh_token(refresh_token)
    # Create new access token using new refesh_data
    new_access_token = create_access_token(refesh_data, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
   
    response.set_cookie('access_token', new_access_token)

    return {"access_token": new_access_token, "token_type": "Bearer"}
    
    

@router.get('/logout', response_model= schemas.Logout)
def logout_remove_token(response: Response, current_user: schemas.User = Depends(get_current_active_user)):
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    response.delete_cookie("token_type")
    return {"status": "success"}