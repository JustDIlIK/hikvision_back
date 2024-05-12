from datetime import datetime

from fastapi import Request, HTTPException, Depends, status
from jose import jwt, JWTError
from starlette.responses import JSONResponse

from app.core.config import settings
from app.db.repositories.users import UsersDAO


def get_token(request: Request):
    token = request.cookies.get("session")
    print(token)
    if not token:
        return JSONResponse(
            status_code=401, content={"detail": "Токен отсутствует"}
        )
    return token


async def get_current_user(token: str = Depends(get_token)):
    try:
        payload = jwt.decode(token, settings.KEY, settings.ALGORITHM)
    except JWTError:
        return JSONResponse(
            status_code=401, content={"detail": "Неверный формат токена"}
        )

    expire: str = payload.get("exp")
    if not expire or int(expire) < datetime.utcnow().timestamp():
        return JSONResponse(
            status_code=401, content={"detail": "Токен истек"}
        )

    user_id: str = payload.get("sub")

    if not user_id:
        return JSONResponse(
            status_code=401, content={"detail": "Неверный логин или пароль"}
        )

    user = await UsersDAO.find_by_id(int(user_id))

    if not user:
        return JSONResponse(
            status_code=401, content={"detail": "Неверный логин или пароль"}
        )

    return user
