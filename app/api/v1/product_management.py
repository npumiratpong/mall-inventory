from fastapi import Depends, APIRouter, Response, HTTPException
from ...models import schemas
from ...service.controller import get_current_active_user

import requests

router = APIRouter()



