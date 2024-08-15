"""Add grade column to student

Revision ID: c38a048575e0
Revises: 9ff68cec15aa
Create Date: 2024-08-16 01:00:13.067011

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c38a048575e0'
down_revision: Union[str, None] = '9ff68cec15aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint(None, 'lessontypes', ['id'])
    op.create_unique_constraint(None, 'parents', ['user_id'])
    op.create_unique_constraint(None, 'payments', ['id'])
    op.create_unique_constraint(None, 'regularlessons', ['id'])
    op.create_unique_constraint(None, 'singlelessons', ['id'])
    op.create_unique_constraint(None, 'singleregularlessons', ['id'])
    op.add_column('students', sa.Column('grade', sa.Integer(), nullable=True))
    op.create_unique_constraint(None, 'students', ['user_id'])
    op.create_unique_constraint(None, 'tutors', ['user_id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'tutors', type_='unique')
    op.drop_constraint(None, 'students', type_='unique')
    op.drop_column('students', 'grade')
    op.drop_constraint(None, 'singleregularlessons', type_='unique')
    op.drop_constraint(None, 'singlelessons', type_='unique')
    op.drop_constraint(None, 'regularlessons', type_='unique')
    op.drop_constraint(None, 'payments', type_='unique')
    op.drop_constraint(None, 'parents', type_='unique')
    op.drop_constraint(None, 'lessontypes', type_='unique')
    # ### end Alembic commands ###
