from shell_helpers import TelegramLogTypes
from data.access.frame.frame_helpers import ConversionTypes
from helpers.generators.generators import Generator
from helpers.logging.console_broadcast import ConsoleBroadcast
from helpers.logging.telegram_bot_broadcast import TelegramBotBroadcast
from helpers.logging.python_logging import PythonLogging
from helpers.logging.null_broadcast import NullBroadcast
from helpers.exceptions import connections_exceptions as connection_excepts
from helpers.exceptions import get_exceptions as get_excepts
from data.connect.csv_connection import CSVConnection
from data.connect.sql_server_connection import SQLServerConnection
from data.connect.mysql_connection import MYSQLConnection
from data.connect.redis_connection import RedisConnection
from data.connect.numpy_connection import NumpyConnection
from data.connect.pickle_connection import PickleConnection
from data.connect.connections_helpers import ConnectionsTypes
from data.access.get.csv_get import CSVGet
from data.access.get.redis_get import RedisGet
from data.access.get.sql_server_get import SQLServerGet
from data.access.get.mysql_get import MYSQLGet
from data.access.frame.pandas_to_rdd_frame import PandasRDDFrame
import pandas


class AIShell:
    def __init__(self, **kwargs):
        self._name = kwargs['name'] if 'name' in kwargs else 'unknown'
        self._log_events = kwargs['log_events'] if 'log_events' in kwargs else True
        self._loggers = [ConsoleBroadcast if self._log_events else NullBroadcast]

        self._generator = Generator()
        self._connections = []
        self._connections_ids = []
        self._connections_names = []
        self._connections_id_to_name_dict = {}
        self._connections_name_to_id_dict = {}
        self._access_objs = []
        self._connection_to_access_dict = {}

        for logger in self._loggers:
            logger.define_framework()

    def set_telegram_logger(self, **kwargs):
        chat_ids = kwargs['chat_ids'] if 'chat_ids' in kwargs else None
        mode = kwargs['mode'] if 'mode' in kwargs else TelegramLogTypes.Telegram_Lite
        self._loggers.append(TelegramBotBroadcast(chat_ids=chat_ids, mode=mode))

    def set_python_logger(self, **kwargs):
        levels = kwargs['levels'] if 'levels' in kwargs else None
        self._loggers.append(PythonLogging(levels=levels, loggers=self._loggers))

    def flush_remainders(self):
        for logger in self._loggers:
            logger.flush()

    # Connection generation
    def generate_connection(self, **kwargs):
        for logger in self._loggers:
            logger.define_connection('start')

        was_successful = True
        connection_type = kwargs['connection_type'] if 'connection_type' in kwargs else None
        connection_name = kwargs['connection_name'] if 'connection_name' in kwargs else None
        connection_name = self.check_on_connection_generation_inputs(connection_type, connection_name)
        connection_id = self._generator.generate_connection_counter()

        if connection_type is ConnectionsTypes.CSV:
            self._connections.append(
                CSVConnection(
                    connection_id=connection_id,
                    connection_type=connection_type,
                    connection_name=connection_name,
                    csv_address=kwargs['csv_address'] if 'csv_address' in kwargs else None,
                    loggers=self._loggers,
                )
            )
        elif connection_type is ConnectionsTypes.NUMPY:
            self._connections.append(
                NumpyConnection(
                    connection_id=connection_id,
                    connection_type=connection_type,
                    connection_name=connection_name,
                    numpy_address=kwargs['numpy_address'] if 'numpy_address' in kwargs else None,
                    loggers=self._loggers
                )
            )
        elif connection_type is ConnectionsTypes.PICKLE:
            self._connections.append(
                PickleConnection(
                    connection_id=connection_id,
                    connection_type=connection_type,
                    connection_name=connection_name,
                    pickle_address=kwargs['pickle_address'] if 'pickle_address' in kwargs else None,
                    loggers=self._loggers
                )
            )
        elif connection_type is ConnectionsTypes.SQL_SERVER:
            self._connections.append(
                SQLServerConnection(
                    connection_id=connection_id,
                    connection_type=connection_type,
                    connection_name=connection_name,
                    username=kwargs['username'] if 'username' in kwargs else None,
                    password=kwargs['password'] if 'password' in kwargs else None,
                    server=kwargs['server'] if 'server' in kwargs else None,
                    database=kwargs['database'] if 'database' in kwargs else None,
                    driver=kwargs['driver'] if 'driver' in kwargs else None,
                    loggers=self._loggers
                )
            )
        elif connection_type is ConnectionsTypes.MY_SQL:
            self._connections.append(
                MYSQLConnection(
                    connection_id=connection_id,
                    connection_type=connection_type,
                    connection_name=connection_name,
                    username=kwargs['username'] if 'username' in kwargs else None,
                    password=kwargs['password'] if 'password' in kwargs else None,
                    server=kwargs['server'] if 'server' in kwargs else None,
                    database=kwargs['database'] if 'database' in kwargs else None,
                    driver=kwargs['driver'] if 'driver' in kwargs else None,
                    port=kwargs['port'] if 'port' in kwargs else None,
                    loggers=self._loggers
                )
            )
        elif connection_type is ConnectionsTypes.REDIS:
            self._connections.append(
                RedisConnection(
                    connection_id=connection_id,
                    connection_type=connection_type,
                    connection_name=connection_name,
                    password=kwargs['password'] if 'password' in kwargs else None,
                    host=kwargs['host'] if 'host' in kwargs else None,
                    port=kwargs['port'] if 'port' in kwargs else None,
                    db_index=kwargs['database_index'] if 'database_index' in kwargs else None,
                    loggers=self._loggers
                )
            )
        else:
            was_successful = False

        if was_successful:
            self._connections_id_to_name_dict[connection_id] = connection_name
            self._connections_name_to_id_dict[connection_name] = connection_id
            self._connections_ids.append(connection_id)
            self._connections_names.append(connection_name)
            self._connection_to_access_dict[connection_id] = None
            for logger in self._loggers:
                logger.print_internal_message(f'connection [{connection_name}] entries are confirmed! Trying to build the connection ...')

            self._connections[-1].build_connection()
            for logger in self._loggers:
                logger.define_connection('end')

    def generate_auto_connection_name(self):
        return f'connection_{self._generator.get_connection_counter()+1}'

    def check_on_connection_generation_inputs(self, connection_type, connection_name):
        try:
            if connection_type is None:
                raise connection_excepts.NoConnectionType(self._loggers)
            elif connection_type not in ConnectionsTypes:
                raise connection_excepts.NoValidConnectionType(self._loggers)
            elif connection_name is None:
                raise connection_excepts.NoConnectionName(self._loggers)
            elif connection_name in self._connections_names:
                raise connection_excepts.DuplicateConnectionName(self._loggers)
            else:
                return connection_name
        except connection_excepts.NoConnectionName as e:
            e.evoke()
            return self.generate_auto_connection_name()
        except connection_excepts.DuplicateConnectionName as e:
            e.evoke()
            return self.generate_auto_connection_name()
        except connection_excepts.ConnectionException as e:
            e.evoke()

    # Getting data
    def get_data(self, **kwargs):
        for logger in self._loggers:
            logger.define_get('start')

        connection_name = kwargs['connection_name'] if 'connection_name' in kwargs else None
        connection_id = kwargs['connection_id'] if 'connection_id' in kwargs else None
        get_query = kwargs['get_query'] if 'get_query' in kwargs else None
        self.check_on_connection_identification_inputs(connection_name, connection_id)
        connection, connection_name, connection_id = self.identify_connection(connection_name, connection_id)

        get_query = self.check_query(get_query, connection.get_type())

        self.generate_access_obj(connection)

        current_cache = self.get_data_from_access_obj(connection, get_query)

        for logger in self._loggers:
            logger.confirm_data_cache(connection_id, connection_name)

        for logger in self._loggers:
            logger.define_get('end')

        return current_cache

    def generate_access_obj(self, connection):
        connection_type = connection.get_type()

        if self._connection_to_access_dict[connection.get_id()] is not None:
            return self._connection_to_access_dict[connection.get_id()]
        else:
            was_successful = True
            if connection_type == ConnectionsTypes.CSV:
                self._access_objs.append(
                    CSVGet(
                        connection_obj=connection.get_connection_obj(),
                        loggers=self._loggers
                    )
                )
            elif connection_type == ConnectionsTypes.REDIS:
                self._access_objs.append(
                    RedisGet(
                        connection_obj=connection.get_connection_obj(),
                        loggers=self._loggers
                    )
                )
            elif connection_type == ConnectionsTypes.SQL_SERVER:
                self._access_objs.append(
                    SQLServerGet(
                        connection_obj=connection.get_connection_obj(),
                        loggers=self._loggers
                    )
                )
            elif connection_type == ConnectionsTypes.MY_SQL:
                self._access_objs.append(
                    MYSQLGet(
                        connection_obj=connection.get_connection_obj(),
                        loggers=self._loggers
                    )
                )
            else:
                was_successful = False

            if was_successful:
                self._connection_to_access_dict[connection.get_id()] = self._access_objs[len(self._access_objs)-1]

    def get_data_from_access_obj(self, connection, query=None):
        if query is not None:
            return self._connection_to_access_dict[connection.get_id()].get_data(query)
        else:
            return self._connection_to_access_dict[connection.get_id()].get_data()

    def get_connection_of_id(self, connection_id):
        return [connection for connection in self._connections if connection.get_id() == connection_id][0]

    def identify_connection(self, connection_name, connection_id):
        if connection_id is None:
            connection_id = self._connections_name_to_id_dict[connection_name]

        connection_name = self._connections_id_to_name_dict[connection_id]

        return self.get_connection_of_id(connection_id), connection_name, connection_id

    def check_on_connection_identification_inputs(self, connection_name, connection_id):
        try:
            if connection_name is None and connection_id is None:
                raise get_excepts.NoIdentification
            if connection_name is not None:
                if not connection_name in self._connections_names:
                    raise get_excepts.InvalidName
            if connection_id is not None:
                if not connection_id in self._connections_ids:
                    raise get_excepts.InvalidID
            if connection_name is not None and connection_id is not None:
                valid_connection_name = self._connections_id_to_name_dict[connection_id]
                if valid_connection_name != connection_name:
                    raise get_excepts.InvalidNameIDPair

        except get_excepts.GetException as e:
            e.evoke()

    def check_query(self, get_query, connection_type):
        try:
            if connection_type is not ConnectionsTypes.CSV and get_query is None:
                raise get_excepts.NoGetQuery
            if connection_type is ConnectionsTypes.CSV and get_query is not None:
                get_query = None
                raise get_excepts.RedundantCSVQuery(self._loggers)

        except get_excepts.GetException as e:
            e.evoke()

        return get_query

    # Framing data
    def frame_data(self, data, subject_type=ConversionTypes.Pandas_Dataframe):
        for logger in self._loggers:
            logger.define_frame('start')

        if isinstance(data, pandas.core.frame.DataFrame):
            convertor = PandasRDDFrame(
                object_type=type(data),
                subject_type=subject_type,
                pandas=data,
                loggers=self._loggers
            )

        framed_data = convertor.frame()

        for logger in self._loggers:
            logger.define_frame('end')

        return framed_data
