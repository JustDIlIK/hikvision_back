from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.db.connection import async_session
from app.db.dbo import BaseDAO
from app.db.models.tg import Area


class AreaDAO(BaseDAO):
    model = Area

    @classmethod
    async def get_all(cls):
        async with async_session() as session:
            query = select(cls.model).options(joinedload(cls.model.groups))
            result = await session.execute(query)
            result = result.unique().scalars().all()

        return result
