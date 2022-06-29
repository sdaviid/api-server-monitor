from fastapi import(
    Depends,
    status,
    APIRouter
)

from app.api.deps import(
    get_current_active_user
)

from app.models.schemas.user import UserDetail


router = APIRouter()



@router.get("/me/", response_model=UserDetail)
async def read_users_me(current_user: str = Depends(get_current_active_user)):
    return current_user


@router.get("/me/items/")
async def read_own_items(current_user: str = Depends(get_current_active_user)):
    return [{"item_id": "Foo", "owner": current_user.username}]