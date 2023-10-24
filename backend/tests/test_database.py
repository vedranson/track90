import os
import pytest
from psycopg2 import connect, Error, OperationalError

TEST_DATABASE_NAME = 'test_database'


@pytest.mark.dependency()
def test_postgres_password_in_environment():
    if 'POSTGRES_PASSWORD' not in os.environ:
        pytest.fail('POSTGRES_PASSWORD not found in environment.')


@pytest.mark.dependency(depends=['test_postgres_password_in_environment'])
def test_postgres_server_access():
    try:
        connect(
            host='localhost',
            port=5432,
            user='postgres',
            password=os.environ.get('POSTGRES_PASSWORD'),
        )
    except Error as e:
        pytest.fail(f'Server access failed {e}')


@pytest.mark.dependency(
    depends=[
        'test_postgres_password_in_environment',
        'test_postgres_server_access'
    ]
)
def test_postgres_server_access_fails_when_nonexistent_user():
    with pytest.raises(OperationalError) as exc_info:
        connect(
            host='localhost',
            port=5432,
            user='the_most_likely_nonexistent_user',
            password=os.environ.get('POSTGRES_PASSWORD'),
        )
    assert str(exc_info.value) == (
        'connection to server at "localhost" (::1), port 5432 failed: '
        'FATAL:  password authentication failed for user '
        '"the_most_likely_nonexistent_user"\n'
    )


@pytest.mark.dependency(depends=['test_postgres_server_access'])
def test_create_drop_databank():
    stmt = "DROP DATABASE IF EXISTS \"%(db_name)s\";"
    try:
        execute_sql(stmt)
    except Error as e:
        pytest.fail(f"Error drop_database_if_exists: {e}")

    stmt = "CREATE DATABASE \"%(db_name)s\";"
    try:
        execute_sql(stmt)
    except Error as e:
        pytest.fail(f"Error create_database: {e}")

    stmt = "DROP DATABASE \"%(db_name)s\";"
    try:
        execute_sql(stmt)
    except Error as e:
        pytest.fail(f"Error drop_database: {e}")


def execute_sql(stmt):
    conn = connect(
        host='localhost',
        port=5432,
        user='postgres',
        password=os.environ.get('POSTGRES_PASSWORD'),
    )
    conn.autocommit = True
    with conn.cursor() as cursor:
        cursor.execute(stmt, {'db_name': TEST_DATABASE_NAME})
