# TODO create config vars using env args from docker-compose.yml
DB_URL = "postgresql+asyncpg://petProjectsUser:password@db:5432/myCodeHedgehogDB"
DB_NAMING_CONVENTION = {
    "ix": 'ix_%(column_0_label)s',
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s"
}
DB_KWARGS = {'echo': True}
