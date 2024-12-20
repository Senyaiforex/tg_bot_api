"""change fields in order

Revision ID: 918aa80842b9
Revises: 86b97cc494d3
Create Date: 2024-12-05 19:41:16.657605

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "918aa80842b9"
down_revision: Union[str, None] = "86b97cc494d3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column(
        "order", sa.Column("description", sa.String(), nullable=True)
    )
    op.add_column("order", sa.Column("date_created", sa.Date(), nullable=True))
    op.alter_column(
        "order", "user_telegram", existing_type=sa.BIGINT(), nullable=True
    )
    op.alter_column(
        "order", "user_name", existing_type=sa.VARCHAR(), nullable=True
    )
    op.alter_column(
        "order", "post_id", existing_type=sa.INTEGER(), nullable=True
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "order", "post_id", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "order", "user_name", existing_type=sa.VARCHAR(), nullable=False
    )
    op.alter_column(
        "order", "user_telegram", existing_type=sa.BIGINT(), nullable=False
    )
    op.drop_column("order", "date_created")
    op.drop_column("order", "description")
    # ### end Alembic commands ###
