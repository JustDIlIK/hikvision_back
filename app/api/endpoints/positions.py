from fastapi import APIRouter, Depends

from app.db.repositories.position import PositionDAO

router = APIRouter(prefix="/positions", tags=["Должности"])


@router.get("/")
async def get_positions():

    positions = await PositionDAO.get_all()

    return positions
