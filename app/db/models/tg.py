from enum import Enum

from sqlalchemy import ForeignKey, Table, Column, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.connection import Base


class Role(Enum):
    admin = "admin"
    spectator = "spectator"
    editor = "editor"


user_device_association = Table(
    "user_device_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("tg_users.id"), primary_key=True),
    Column("device_id", Integer, ForeignKey("devices.id"), primary_key=True),
)

user_area_association = Table(
    "user_areas_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("tg_users.id"), primary_key=True),
    Column("area_id", Integer, ForeignKey("areas.id"), primary_key=True),
)


class Area(Base):
    __tablename__ = "areas"

    name: Mapped[str]
    own_id: Mapped[str]

    users = relationship(
        "TgUser", secondary=user_area_association, back_populates="areas"
    )
    groups = relationship("Group", backref="areas")

    def __str__(self):
        return f"{self.name}"


class Device(Base):
    __tablename__ = "devices"

    name: Mapped[str]
    serial_name: Mapped[str]
    own_id: Mapped[str]
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"), nullable=False)
    area = relationship("Area", backref="devices")

    users = relationship(
        "TgUser", secondary=user_device_association, back_populates="devices"
    )

    def __str__(self):
        return f"{self.name}"


class Group(Base):
    __tablename__ = "groups"

    name: Mapped[str]
    own_id: Mapped[str]
    area_id: Mapped[int] = mapped_column(ForeignKey("areas.id"), nullable=True)

    def __str__(self):
        return f"{self.name}"


class TgUser(Base):
    __tablename__ = "tg_users"

    tg_id: Mapped[str]
    name: Mapped[str]
    role: Mapped[Role]
    areas = relationship(
        "Area", secondary=user_area_association, back_populates="users"
    )
    devices = relationship(
        "Device", secondary=user_device_association, back_populates="users"
    )

    def __str__(self):
        return f"{self.name}"
