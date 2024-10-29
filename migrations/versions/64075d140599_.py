"""empty message

Revision ID: 64075d140599
Revises: 678051e507fe
Create Date: 2024-10-29 23:50:45.589385

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '64075d140599'
down_revision = '678051e507fe'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=mysql.VARCHAR(length=128),
               type_=sa.String(length=255),
               existing_nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('users', schema=None) as batch_op:
        batch_op.alter_column('password_hash',
               existing_type=sa.String(length=255),
               type_=mysql.VARCHAR(length=128),
               existing_nullable=False)

    # ### end Alembic commands ###
