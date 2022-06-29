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
        options = {"verify_signature": True, "verify_aud": False, "exp": True}
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options=options)
        username: str = payload.get("sub")
        if username is None:
            print('aki1')
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        print('aki2')
        raise credentials_exception
    audience = payload.get('aud')
    if not audience == 'cli-web-monitor':
        print(payload.get('aud'))
        print('aki3')
        raise credentials_exception
    return payload.get('sub')


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user