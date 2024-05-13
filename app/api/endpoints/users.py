from fastapi import APIRouter
from starlette.responses import Response, JSONResponse

from app.api.services.auth import (
    get_hashed_password,
    create_access_token,
    authenticate_user,
)
from app.db.repositories.users import UsersDAO

from app.db.schemas.users import SUsersAuthLogin

router = APIRouter(prefix=("/auth"), tags=["Пользователь"])

#
# @router.post("/register")
# async def register_user(user_data: SUsersAuthLogin):
#     existing_user = await UsersDAO.find_one_or_none(email=user_data.email)
#     if existing_user:
#         return JSONResponse(
#             status_code=409, content={"detail": "Данная почта уже была использована"}
#         )
#
#     password = get_hashed_password(user_data.password)
#     user_data.password = password
#     await UsersDAO.add_record(email=user_data.email, password=user_data.password)


@router.post("/login")
async def login_user(response: Response, user_data: SUsersAuthLogin):
    user = await authenticate_user(user_data.email, user_data.password)
    print(user)
    if not user:
        return JSONResponse(
            status_code=401, content={"detail": "Неверный логин или пароль"}
        )

    access_token = create_access_token({"sub": str(user.id)})
    response.set_cookie("token", access_token)
    return access_token


@router.post("/logout")
async def login_user(response: Response):
    response.delete_cookie("token")


@router.get("/get-users")
async def get_users():
    users = await UsersDAO.get_all()

    return users
