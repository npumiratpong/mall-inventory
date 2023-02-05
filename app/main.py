
import sys
sys.path.append(".")

from typing import Union, Optional, List, Dict
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from sqlalchemy.orm import Session
from starlette.middleware.cors import CORSMiddleware

from models import schemas
from service import database_connection
from service.database import SessionLocal
from service.controller import get_current_active_user, get_db

from api.v1 import auth, search

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
app.include_router(search.router, tags=['search'], prefix='/api/v1/search')

@app.get("/users/{username}", response_model=schemas.User)
def get_user_in_db(username: str = Depends(get_current_active_user), db: Session = Depends(get_db)):
    db_user = database_connection.get_user_by_username(db, username=username)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user