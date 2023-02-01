"""initial migration

Revision ID: da4ba4fa0dca
Revises: 
Create Date: 2023-01-31 15:14:58.321618

"""
from alembic import op
import sqlalchemy as sa
import flask_security


# revision identifiers, used by Alembic.
revision = 'da4ba4fa0dca'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Customers',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('GivenName', sa.String(length=50), nullable=False),
    sa.Column('Surname', sa.String(length=50), nullable=False),
    sa.Column('Streetaddress', sa.String(length=50), nullable=False),
    sa.Column('City', sa.String(length=50), nullable=False),
    sa.Column('Zipcode', sa.String(length=10), nullable=False),
    sa.Column('Country', sa.String(length=30), nullable=False),
    sa.Column('CountryCode', sa.String(length=2), nullable=False),
    sa.Column('Birthday', sa.DateTime(), nullable=False),
    sa.Column('NationalId', sa.String(length=20), nullable=False),
    sa.Column('TelephoneCountryCode', sa.Integer(), nullable=False),
    sa.Column('Telephone', sa.String(length=20), nullable=False),
    sa.Column('EmailAddress', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_table('role',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=80), nullable=False),
    sa.Column('description', sa.String(length=255), nullable=True),
    sa.Column('permissions', flask_security.datastore.AsaList(), nullable=True),
    sa.Column('update_datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(length=255), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=False),
    sa.Column('fs_uniquifier', sa.String(length=64), nullable=False),
    sa.Column('confirmed_at', sa.DateTime(), nullable=True),
    sa.Column('last_login_at', sa.DateTime(), nullable=True),
    sa.Column('current_login_at', sa.DateTime(), nullable=True),
    sa.Column('last_login_ip', sa.String(length=64), nullable=True),
    sa.Column('current_login_ip', sa.String(length=64), nullable=True),
    sa.Column('login_count', sa.Integer(), nullable=True),
    sa.Column('tf_primary_method', sa.String(length=64), nullable=True),
    sa.Column('tf_totp_secret', sa.String(length=255), nullable=True),
    sa.Column('tf_phone_number', sa.String(length=128), nullable=True),
    sa.Column('create_datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('update_datetime', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.Column('username', sa.String(length=255), nullable=True),
    sa.Column('us_totp_secrets', sa.Text(), nullable=True),
    sa.Column('fs_webauthn_user_handle', sa.String(length=64), nullable=True),
    sa.Column('mf_recovery_codes', flask_security.datastore.AsaList(), nullable=True),
    sa.Column('password', sa.String(length=255), nullable=True),
    sa.Column('us_phone_number', sa.String(length=128), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('fs_uniquifier'),
    sa.UniqueConstraint('fs_webauthn_user_handle'),
    sa.UniqueConstraint('us_phone_number'),
    sa.UniqueConstraint('username')
    )
    op.create_table('Accounts',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('AccountType', sa.String(length=10), nullable=False),
    sa.Column('Created', sa.DateTime(), nullable=False),
    sa.Column('Balance', sa.Integer(), nullable=False),
    sa.Column('CustomerId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['CustomerId'], ['Customers.Id'], ),
    sa.PrimaryKeyConstraint('Id')
    )
    op.create_table('roles_users',
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], )
    )
    op.create_table('Transactions',
    sa.Column('Id', sa.Integer(), nullable=False),
    sa.Column('Type', sa.String(length=20), nullable=False),
    sa.Column('Operation', sa.String(length=50), nullable=False),
    sa.Column('Date', sa.DateTime(), nullable=False),
    sa.Column('Amount', sa.Integer(), nullable=False),
    sa.Column('NewBalance', sa.Integer(), nullable=False),
    sa.Column('AccountId', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['AccountId'], ['Accounts.Id'], ),
    sa.PrimaryKeyConstraint('Id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Transactions')
    op.drop_table('roles_users')
    op.drop_table('Accounts')
    op.drop_table('user')
    op.drop_table('role')
    op.drop_table('Customers')
    # ### end Alembic commands ###
