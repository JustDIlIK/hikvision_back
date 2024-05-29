from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import Base


class Position(Base):
    __tablename__ = "positions"

    title: Mapped[str] = mapped_column(unique=True)
