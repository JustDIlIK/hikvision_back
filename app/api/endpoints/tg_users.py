from fastapi import APIRouter

from app.db.repositories.tgUser import TgUserDAO

router = APIRouter(prefix="/tg-users", tags=["Тг пользователи"])


@router.get("/")
async def get_all():
    data = await TgUserDAO.get_all()

    return data


@router.get("/detail/{tg_id}/")
async def get_all(tg_id: str):
    data = await TgUserDAO.get_by_tg_id(tg_id=tg_id)

    return data
