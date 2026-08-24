"""add cafe and hotel to local service category

Revision ID: c57569b81b09
Revises: 2e1fdaf99c5d
Create Date: 2026-08-24 18:57:12.823005

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c57569b81b09'
down_revision: Union[str, None] = '2e1fdaf99c5d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new enum values to PostgreSQL ENUM type.
    # Note: ALTER TYPE ... ADD VALUE cannot be executed inside a transaction block, 
    # so we must set `connection.execution_options(isolation_level="AUTOCOMMIT")` if needed, 
    # but alembic often handles simple ALTER TYPE if we use `commit()`.
    op.execute("ALTER TYPE local_service_category ADD VALUE IF NOT EXISTS 'cafe'")
    op.execute("ALTER TYPE local_service_category ADD VALUE IF NOT EXISTS 'hotel'")


def downgrade() -> None:
    # Downgrading enum values in Postgres is non-trivial (requires recreating type)
    # Since this is local/dev and harmless, we'll leave it as a no-op for now.
    pass
