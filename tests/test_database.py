import pytest

from clipmanager.database import Database


@pytest.fixture(scope='function')
def database():
    db = Database()
    yield db
    db.close()


class TestDatabase:
    def test_open(self, database):
        assert database.open()
        assert not database.connection.isOpenError()

    def test_close(self, database):
        assert not database.close()

    def test_driver(self, database):
        assert database.connection.isDriverAvailable('QSQLITE')
        assert database.connection.driverName() == 'QSQLITE'

    def test_create_tables(self, database):
        assert database.create_tables()
        assert database.connection.isValid()
