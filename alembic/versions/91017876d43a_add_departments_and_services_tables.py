from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = '91017876d43a'
down_revision: Union[str, None] = 'cbe772ef7868'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create departments table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'departments'):
        op.create_table(
            'departments',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String, index=True)
        )

    # Create services table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'services'):
        op.create_table(
            'services',
            sa.Column('id', sa.Integer, primary_key=True),
            sa.Column('name', sa.String, index=True),
            sa.Column('department_id', sa.Integer, sa.ForeignKey('departments.id'))
        )

    # Create contract_departments table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'contract_departments'):
        op.create_table(
            'contract_departments',
            sa.Column('contract_id', sa.Integer, sa.ForeignKey('contracts.id'), primary_key=True),
            sa.Column('department_id', sa.Integer, sa.ForeignKey('departments.id'), primary_key=True)
        )

    # Create contract_services table if it doesn't exist
    if not op.get_bind().dialect.has_table(op.get_bind(), 'contract_services'):
        op.create_table(
            'contract_services',
            sa.Column('contract_id', sa.Integer, sa.ForeignKey('contracts.id'), primary_key=True),
            sa.Column('service_id', sa.Integer, sa.ForeignKey('services.id'), primary_key=True)
        )

    # Drop the old services column from the contracts table
    op.drop_column('contracts', 'services')


def downgrade() -> None:
    # Recreate the old services column in the contracts table
    op.add_column('contracts', sa.Column('services', sa.String(), nullable=True))

    # Drop contract_services table if it exists
    if op.get_bind().dialect.has_table(op.get_bind(), 'contract_services'):
        op.drop_table('contract_services')

    # Drop contract_departments table if it exists
    if op.get_bind().dialect.has_table(op.get_bind(), 'contract_departments'):
        op.drop_table('contract_departments')

    # Drop services table if it exists
    if op.get_bind().dialect.has_table(op.get_bind(), 'services'):
        op.drop_table('services')

    # Drop departments table if it exists
    if op.get_bind().dialect.has_table(op.get_bind(), 'departments'):
        op.drop_table('departments')
