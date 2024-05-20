"""Changing adding foreignkey to device

Revision ID: 34addbbe869a
Revises: 7c5d321de471
Create Date: 2024-05-20 15:03:37.522139

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '34addbbe869a'
down_revision: Union[str, None] = '7c5d321de471'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('groups', sa.Column('area_id', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'groups', 'areas', ['area_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'groups', type_='foreignkey')
    op.drop_column('groups', 'area_id')
    # ### end Alembic commands ###
