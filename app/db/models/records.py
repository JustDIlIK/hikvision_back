from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import Base


class Record(Base):
    __tablename__ = "records"

    record_id: Mapped[str] = mapped_column(unique=True)
