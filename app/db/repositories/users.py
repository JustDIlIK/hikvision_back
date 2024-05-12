from sqlalchemy import select

from app.db.connection import async_session
from app.db.dbo import BaseDAO
from app.db.models.users import User


class UsersDAO(BaseDAO):
    model = User

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.scalar()
