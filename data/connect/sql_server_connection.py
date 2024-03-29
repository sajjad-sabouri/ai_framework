from data.connect.sql_database_connection import SQLDatabaseConnection
from helpers.exceptions import connections_exceptions as excepts
import pyodbc


class SQLServerConnection(SQLDatabaseConnection):
    def __init__(self, **kwargs):
        super(SQLServerConnection, self).__init__(**kwargs)
        self._driver = kwargs['driver'] if 'driver' in kwargs else None
        self.check_on_construction_inputs()

    def check_on_construction_inputs(self):
        super(SQLServerConnection, self).check_on_construction_inputs()
        try:
            if self._driver is None:
                raise excepts.NoMSSQLServerDriver(self._loggers)
        except excepts.ConnectionException as e:
            e.evoke()
        except:
            excepts.VitalConnectionException(self._loggers).evoke()

    def build_connection(self):
        try:
            self._connection_obj = pyodbc.connect(
                f'DRIVER={self._driver};' +
                f'SERVER={self._server};' +
                f'DATABASE={self._database};' +
                f'UID={self._username};' +
                f'PWD={self._password}'
                # autocommit=True -> I don't know what this does. Needs to be checked.
            )
        except pyodbc.Error as e:
            excepts.RelationalDBConnectionError(self._loggers).evoke(f"Pyodbc error code: {e.args[0]} | error description: {e.args[1]}!")
        except Exception as e:
            excepts.VitalConnectionException(self._loggers).evoke(e)
        finally:
            pass

        super(SQLServerConnection, self).build_connection()
