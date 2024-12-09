from bson import ObjectId
from fastapi import FastAPI, HTTPException, Depends
from fastapi.responses import JSONResponse
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional
import httpx
from pydantic import BaseModel, Field


class CommonHeaders(BaseModel):
    Authorization: str


class FlightTicket(BaseModel):
    id: str = Field(default_factory=lambda: str(ObjectId()), alias="_id")
    flight_number: str
    passenger_name: str
    destination: str
    price: float
    user_id: Optional[int] = None
    timestamp: Optional[str] = None


class User(BaseModel):
    id: int = Field(alias="_id")
    name: Optional[str] = None
    email: Optional[str] = None
    registered_objects: int = 0


SECRET_KEY = "5db8fb310ffbe27ed0f1afd5c12de11b65694ed79cb2e12d4f5180c12ac5c8dc"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

app = FastAPI()

USER_SERVICE_URL = "http://user_service:8001"
FLIGHT_TICKET_SERVICE_URL = "http://flight_ticket_service:8000"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token", )


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != "admin" or form_data.password != "password":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    access_token = create_access_token(data={"sub": form_data.username})
    return {"access_token": access_token, "token_type": "bearer"}


@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{USER_SERVICE_URL}/users/{user_id}")
        return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/users", response_model=User)
async def create_user(user: User, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{USER_SERVICE_URL}/users", json=user.model_dump(by_alias=True))
        return JSONResponse(content=response.json(), status_code=response.status_code)


@app.get("/tickets/{ticket_id}", response_model=FlightTicket)
async def get_ticket(ticket_id: str, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{FLIGHT_TICKET_SERVICE_URL}/tickets/{ticket_id}")
        return JSONResponse(content=response.json(), status_code=response.status_code)


@app.post("/tickets", response_model=FlightTicket)
async def create_ticket(ticket: FlightTicket, token: str = Depends(oauth2_scheme)):
    verify_token(token)
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{FLIGHT_TICKET_SERVICE_URL}/tickets", json=ticket.model_dump(by_alias=True))
        return JSONResponse(content=response.json(), status_code=response.status_code)
