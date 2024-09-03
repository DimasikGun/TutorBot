"""Add Notes table

Revision ID: d08960abe957
Revises: aa76937d9178
Create Date: 2024-09-04 01:14:07.913615

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd08960abe957'
down_revision: Union[str, None] = 'aa76937d9178'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('notes',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('tutor', sa.BigInteger(), nullable=False),
    sa.Column('student', sa.BigInteger(), nullable=False),
    sa.Column('text', sa.String(length=256), nullable=False),
    sa.Column('user_id', sa.BigInteger(), autoincrement=False, nullable=False),
    sa.Column('username', sa.String(length=32), nullable=True),
    sa.Column('name', sa.String(length=32), nullable=False),
    sa.Column('surname', sa.String(length=32), nullable=False),
    sa.Column('phone', sa.String(length=16), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['student'], ['students.user_id'], ),
    sa.ForeignKeyConstraint(['tutor'], ['tutors.user_id'], ),
    sa.PrimaryKeyConstraint('id', 'user_id'),
    sa.UniqueConstraint('id'),
    sa.UniqueConstraint('user_id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('notes')
    # ### end Alembic commands ###
