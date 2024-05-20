from sqlalchemy import select

from app.db.connection import async_session
from app.db.dbo import BaseDAO
from app.db.models.records import Record


class RecordDAO(BaseDAO):
    model = Record

    @classmethod
    async def get_last(cls):

        async with async_session() as session:
            query = select(cls.model).order_by(cls.model.id.desc())
            result = await session.execute(query)
            return result.scalar()
