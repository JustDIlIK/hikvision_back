from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.connection import async_session
from app.db.dbo import BaseDAO
from app.db.models.tg import TgUser, Device, Area


class TgUserDAO(BaseDAO):
    model = TgUser

    @classmethod
    async def get_all(cls):

        async with async_session() as session:
            query = (
                select(cls.model)
                .options(joinedload(cls.model.areas).joinedload(Area.groups))
                .options(joinedload(cls.model.devices))
            )
            result = await session.execute(query)

            return result.scalars().unique().all()

    @classmethod
    async def get_by_tg_id(cls, tg_id):
        async with async_session() as session:
            query = (
                select(cls.model)
                .options(joinedload(cls.model.areas).joinedload(Area.groups))
                .options(joinedload(cls.model.devices))
                .where(cls.model.tg_id == tg_id)
            )
            result = await session.execute(query)
            return result.scalar()
