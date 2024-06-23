import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '8346d90a9476'
down_revision = '91017876d43a'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('companies', sa.Column('logo_url', sa.String(), nullable=True))
    op.drop_column('companies', 'logo')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('companies', sa.Column('logo', sa.String(), nullable=True))
    op.drop_column('companies', 'logo_url')
    # ### end Alembic commands ###
