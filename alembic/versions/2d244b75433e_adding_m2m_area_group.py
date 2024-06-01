"""Adding m2m area-group

Revision ID: 2d244b75433e
Revises: bdeee580e67f
Create Date: 2024-06-01 19:04:36.780899

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d244b75433e'
down_revision: Union[str, None] = 'bdeee580e67f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('group_areas_association',
    sa.Column('group_id', sa.Integer(), nullable=False),
    sa.Column('area_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['area_id'], ['areas.id'], ),
    sa.ForeignKeyConstraint(['group_id'], ['groups.id'], ),
    sa.PrimaryKeyConstraint('group_id', 'area_id')
    )
    op.drop_constraint('groups_area_id_fkey', 'groups', type_='foreignkey')
    op.drop_column('groups', 'area_id')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('groups', sa.Column('area_id', sa.INTEGER(), autoincrement=False, nullable=True))
    op.create_foreign_key('groups_area_id_fkey', 'groups', 'areas', ['area_id'], ['id'])
    op.drop_table('group_areas_association')
    # ### end Alembic commands ###
