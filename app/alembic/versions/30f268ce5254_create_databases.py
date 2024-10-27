"""create databases

Revision ID: e931bc880e7d
Revises: 
Create Date: 2024-04-24 21:55:59.097232

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '30f268ce5254'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


# Define the upgrade and downgrade functions
def upgrade():
    op.create_table(
        'task',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_creator_id', sa.Integer(), nullable=False),
        sa.Column('task_executor_id', sa.Integer(), nullable=False),
        sa.Column('task_name', sa.String(length=255), nullable=False),
        sa.Column('subtask_name', sa.String(length=255)),
        sa.Column('task_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.Column('deadline', sa.TIMESTAMP()),
        sa.Column('state', sa.Boolean(), nullable=True),
        sa.Column('comment', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=255), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('telegram_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.TIMESTAMP(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('role_name', sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'task_assignments',
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('task_executor_id', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ),
        sa.ForeignKeyConstraint(['task_executor_id'], ['users.id'], )
    )


def downgrade():
    op.drop_table('task_assignments')
    op.drop_table('roles')
    op.drop_table('users')
    op.drop_table('task')