"""update_type_field_update

Revision ID: 18aec85b793c
Revises: 62069051cae6
Create Date: 2024-10-01 22:44:41.814776

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "18aec85b793c"
down_revision: Union[str, None] = "62069051cae6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users",
        "count_free_posts",
        existing_type=sa.INTEGER(),
        nullable=False,
        existing_comment="Количество бесплатных размещённых постов",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "users",
        "count_free_posts",
        existing_type=sa.INTEGER(),
        nullable=True,
        existing_comment="Количество бесплатных размещённых постов",
    )
    # ### end Alembic commands ###