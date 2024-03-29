from helpers.exceptions import connections_exceptions as excepts


class Connection:
    def __init__(self, **kwargs):
        self._loggers = kwargs['loggers'] if 'loggers' in kwargs else []
        self._connection_id = kwargs['connection_id'] if 'connection_id' in kwargs else None
        self._connection_name = kwargs['connection_name'] if 'connection_name' in kwargs else None
        self._connection_type = kwargs['connection_type'] if 'connection_type' in kwargs else None
        self._connection_obj = None

    def check_on_construction_inputs(self):
        try:
            if self._connection_id is None:
                raise excepts.NoIDError
        except excepts.ConnectionException.evoke() as e:
            e.evoke()
        except:
            excepts.VitalConnectionException().evoke()
        finally:
            pass

    def build_connection(self):
        for logger in self._loggers:
            logger.confirm_connection(self._connection_id, self._connection_name)

    def get_id(self):
        return self._connection_id

    def get_type(self):
        return self._connection_type

    def get_connection_obj(self):
        return self._connection_obj
