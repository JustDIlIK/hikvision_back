from sqladmin import ModelView

from app.db.models.positions import Position
from app.db.models.records import Record
from app.db.models.tg import Area, Device, TgUser, Group
from app.db.models.users import User


class UserAdmin(ModelView, model=User):
    column_list = [User.id, User.email]
    column_details_exclude_list = [User.password]
    can_delete = False
    can_edit = False
    icon = "fa-solid fa-user"


class AreasAdmin(ModelView, model=Area):
    column_list = [c.name for c in Area.__table__.c]
    icon = "fa-solid fa-trophy"


class DevicesAdmin(ModelView, model=Device):
    column_list = [c.name for c in Device.__table__.c]
    icon = "fa-solid fa-trophy"


class TgUsersAdmin(ModelView, model=TgUser):
    column_list = [c.name for c in TgUser.__table__.c] + [TgUser.devices]
    icon = "fa-solid fa-trophy"


class GroupsAdmin(ModelView, model=Group):
    column_list = [c.name for c in Group.__table__.c]
    icon = "fa-solid fa-trophy"


class RecordsAdmin(ModelView, model=Record):
    column_list = [c.name for c in Record.__table__.c]
    icon = "fa-solid fa-trophy"


class PositionsAdmin(ModelView, model=Position):
    column_list = [c.name for c in Position.__table__.c]
    icon = "fa-solid fa-trophy"
