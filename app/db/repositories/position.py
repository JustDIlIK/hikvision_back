from app.db.dbo import BaseDAO
from app.db.models.positions import Position


class PositionDAO(BaseDAO):
    model = Position
