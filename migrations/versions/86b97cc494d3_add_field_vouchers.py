"""add field - vouchers

Revision ID: 86b97cc494d3
Revises: 584545436fc9
Create Date: 2024-12-03 21:38:09.964707

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "86b97cc494d3"
down_revision: Union[str, None] = "584545436fc9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "users",
        sa.Column(
            "vouchers",
            sa.Integer(),
            nullable=True,
            comment="Количество купленных ваучеров",
        ),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "vouchers")
    # ### end Alembic commands ###
