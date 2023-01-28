from typing import Union, Optional, List, Dict
from datetime import datetime, timedelta

from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware

SECRET_KEY = "4757a5228c03cece3cfd8ce77e05e1769597b94bf416d934120bb0720c91f3ba"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

fake_users_db = {
    "johndoe": {
        "user_id": 10001,
        "username": "johndoe",
        "first_name": "John",
        "last_name": "Doe",
        "email": "johndoe@example.com",
        "modified_when": datetime.utcnow(),
        "created_when": datetime.utcnow(),
        "hashed_password": "$2y$10$Oii4iPEwk8MIQ2wp0WOdq.7XGMneEUOMUtq6aj/lp7rPQnTJLZVZy",
        "role": 'admin',
        "is_active": True,
    },
    "jason": {
        "user_id": 10001,
        "username": "jason",
        "first_name": "Jason",
        "last_name": "Doe",
        "email": "jason@example.com",
        "modified_when": datetime.utcnow(),
        "created_when": datetime.utcnow(),
        "hashed_password": "$2y$10$Oii4iPEwk8MIQ2wp0WOdq.7XGMneEUOMUtq6aj/lp7rPQnTJLZVZy",
        "role": 'sell_store',
        "is_active": True,
    },
    "alice": {
        "user_id": 10002,
        "username": "alice",
        "first_name": "Alice",
        "last_name": "Wonderson",
        "email": "alice@example.com",
        "modified_when": datetime.utcnow(),
        "created_when": datetime.utcnow(),
        "hashed_password": "$2y$10$0u4H13Xn/BOJ2VvN12vZkepP4FbRAClUnazWhm3xmeynPK6gw3Apy",
        "role": 'sell_store',
        "is_active": False,
    }
}

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str

class TokenData(BaseModel):
    username: Union[str, None] = None

class User(BaseModel):
    user_id: int
    username: str
    first_name: Union[str, None] = None
    last_name: Union[str, None] = None
    email: Union[str, None] = None
    modified_when: Union[datetime, None] = None
    created_when: Union[datetime, None] = None
    role: Union[str, None] = None
    is_active: Union[bool, None] = None

class UserInDB(User):
    hashed_password: str

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return UserInDB(**user_dict)

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

def create_access_token(data: dict, expires_delta: Union[timedelta, None] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=403, detail="Inactive User")
    return current_user

@app.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive User")
    elif not user:
        raise HTTPException(
            status_code=401, 
            detail= "Incorrect Username or Password",
            headers= {"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer", "role": user.role}

@app.get("/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.get("/users/me/items/")
async def read_own_items(current_user: User = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]