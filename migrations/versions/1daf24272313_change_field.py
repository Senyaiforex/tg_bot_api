"""change_field

Revision ID: 1daf24272313
Revises: 918aa80842b9
Create Date: 2024-12-15 12:45:58.549680

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "1daf24272313"
down_revision: Union[str, None] = "918aa80842b9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "changes_transactions",
        sa.Column("from_currency", sa.String(), nullable=False),
    )
    op.drop_column("changes_transactions", "from_сurrency")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "changes_transactions",
        sa.Column(
            "from_сurrency", sa.VARCHAR(), autoincrement=False, nullable=False
        ),
    )
    op.drop_column("changes_transactions", "from_currency")
    # ### end Alembic commands ###
