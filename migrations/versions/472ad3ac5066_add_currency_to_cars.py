"""add currency to cars

Revision ID: 472ad3ac5066
Revises: 2a205019e260
Create Date: 2025-10-24 16:34:43.185819

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '472ad3ac5066'
down_revision = '2a205019e260'
branch_labels = None
depends_on = None


def upgrade():
    # 1) Добавляем колонку с server_default, чтобы прошёл NOT NULL на существующих строках
    op.add_column(
        'cars',
        sa.Column('currency', sa.String(length=3), nullable=False, server_default='RUB')
    )
    # 2) На всякий случай заполняем NULL (если вдруг где-то они могли появиться)
    op.execute("UPDATE cars SET currency = 'RUB' WHERE currency IS NULL;")
    # 3) Убираем server_default, чтобы база дальше не навязывала RUB сама (будет работать дефолт приложения/ORM)
    op.alter_column('cars', 'currency', server_default=None)

def downgrade():
    op.drop_column('cars', 'currency')
