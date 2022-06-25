from datetime import datetime, timedelta

from fastapi import(
    HTTPException,
    Depends,
    status,
    APIRouter
)
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.config import(
    ACCESS_TOKEN_EXPIRE_MINUTES
)
from app.api.deps import(
    fake_users_db,
    Token,
    User,
    authenticate_user,
    create_access_token,
    get_current_active_user
)

router = APIRouter()




@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.user}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

