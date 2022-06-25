from datetime import datetime, timedelta
from typing import Union

from fastapi import(
    Depends,
    HTTPException,
    status
)
from fastapi.security import(
    OAuth2PasswordBearer,
    OAuth2PasswordRequestForm
)
from jose import(
    JWTError,
    jwt
)
from pydantic import BaseModel

from app.config import(
    SECRET_KEY,
    ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.models.schemas.user import UserDetail
from app.models.schemas.token import(
    Token,
    TokenData
)
from app.models.domain.user import User
from app.core.database import SessionLocal

fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "password": "123456",
        "disabled": False,
    }
}







oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")





def authenticate_user(username: str, password: str):
    response_user = User.check_login(session=SessionLocal(), user=username, password=password)
    if not response_user:
        return False
    return response_user[0]


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
    user = User.get_user(session=SessionLocal(), user=token_data.username)
    if user is None:
        raise credentials_exception
    return user[0]


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user