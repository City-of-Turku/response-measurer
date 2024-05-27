from abc import ABC, abstractmethod

class DriverType:
    DEFAULT = 'default'
    POSTGRES = 'postgres'

    @classmethod
    def find(cls, driver_str):
        if driver_str.lower().startswith(cls.POSTGRES):
            return cls.POSTGRES
        return cls.DEFAULT

class Driver(ABC):
    def __init__(self, driver_str):
        if not hasattr(self, '_initialized'):
            self.driver_str = driver_str
            self.type = DriverType.find(self.driver_str)
            setattr(self, '_initialized', True)

    def __new__(cls, driver_str):
        driver_type = DriverType.find(driver_str)
        if driver_type == DriverType.POSTGRES:
            return super(Driver, PostgreSQL).__new__(PostgreSQL)
        else:
            return super(Driver, Default).__new__(Default)

    @abstractmethod
    def get_query_str(self, table):
        pass


class Default(Driver):
    def get_query_str(self, table):
        return f'SELECT TOP 10 * FROM {table} ORDER BY NEWID();'


class PostgreSQL(Driver):
    def get_query_str(self, table):
        return f'SELECT * FROM {table} ORDER BY id desc limit 10;'
