"""Changing db (adding index to Records)

Revision ID: a5606e465822
Revises: 2d244b75433e
Create Date: 2024-06-01 19:18:54.269110

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a5606e465822'
down_revision: Union[str, None] = '2d244b75433e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('records_record_id_key', 'records', type_='unique')
    op.create_index(op.f('ix_records_object_id'), 'records', ['object_id'], unique=False)
    op.create_index(op.f('ix_records_record_id'), 'records', ['record_id'], unique=True)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_records_record_id'), table_name='records')
    op.drop_index(op.f('ix_records_object_id'), table_name='records')
    op.create_unique_constraint('records_record_id_key', 'records', ['record_id'])
    # ### end Alembic commands ###