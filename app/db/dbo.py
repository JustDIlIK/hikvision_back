from sqlalchemy import select, insert, delete

from app.db.connection import async_session


class BaseDAO:
    model = None

    @classmethod
    async def get_all(cls):
        async with async_session() as session:
            query = select(cls.model).order_by(cls.model.id)
            result = await session.execute(query)
            return result.scalars().all()

    @classmethod
    async def add_record(cls, **data):
        async with async_session() as session:
            query = insert(cls.model).values(data).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalar()

    @classmethod
    async def find_by_id(cls, record_id):
        async with async_session() as session:
            query = select(cls.model).filter_by(id=record_id)
            result = await session.execute(query)
            return result.scalar()

    @classmethod
    async def find_one_or_none(cls, **filter_by):
        async with async_session() as session:
            query = select(cls.model).filter_by(**filter_by)
            result = await session.execute(query)
            return result.first()

    @classmethod
    async def remove_by_id(cls, record_id):
        async with async_session() as session:
            query = delete(cls.model).filter_by(id=record_id).returning(cls.model)
            result = await session.execute(query)
            await session.commit()
            return result.scalar()
