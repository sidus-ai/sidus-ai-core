#############################################################
# Classes - environments
#############################################################
import sidusai.core.utils as utils


class AgentValue:
    """
    An abstract wrapper for the processed data
    """

    def __init__(self):
        pass


class AgentTask:
    """
    An abstract wrapper for the tasks available to the agent
    """

    def __init__(self):
        """
        """
        pass

    def forward(self, *args, **kwargs) -> AgentValue:
        """
        The method should wrap the data in a predefined object for further use.
        :return:
        """
        pass

    def on_complete(self, value: AgentValue, *args, **kwargs) -> None:
        """
        Getting the final result after transformations of the skill graph
        :param value:
        :return:
        """
        pass


#############################################################
# Helper classes - data types
#############################################################

class TaskContainer:
    """
    Graph caching configuration for a registered task
    """

    def __init__(self, task_type: type, task_name: str, available_skill_name: [str]):
        self.task_type = task_type
        self.task_name = task_name
        self.available_skill_names = available_skill_name

        self.skill_graph = None
        self.executable_init = None


class LoopContainer:
    """
    Container of reproducible methods in the main loop of the application
    """

    def __init__(self, executable, fixed_interval_sec: int | None):
        self.order = executable.order
        self.fixed_interval_sec = fixed_interval_sec
        self.executable = executable

        self.last_loop_at = utils.current_sec()
        self.is_executing = False


class ExceptionHandlerContainer:

    def __init__(self, executable, error_types: list = None):
        if error_types is None:
            error_types = []
        self.order = executable.order
        self.error_types = error_types
        self.executable = executable


class NamedTypedContainer:
    """
    A container that provides access to content by name or by object type.
    Don't use primitive data types for storage in container
    """

    def __init__(self):
        self.container = []

        self.types = {}
        self.names = {}

    def put(self, obj, key, _type: type = None):
        """
        Put object to container
        :param _type: Object type
        :param obj:  object
        :param key: custom object name
        :return:
        """
        if key is None:
            raise ValueError('Key in container can not be None')

        if obj is None:
            raise ValueError('Object in container can not be None')

        if _type is None:
            _type = self._get_type_from_object(obj)

        _index_type = self._get_index(_type)
        _index_key = self._get_index(key)

        if _index_key != _index_type and _index_type is not None and _index_key is not None:
            raise ValueError('An object of this type is already registered under a different name.')

        if _index_key is not None and _index_type is None:
            raise ValueError('Another object with the same name is already registered.')

        if _index_key is None and _index_type is not None:
            raise ValueError('An object of this type is already registered under a different name.')

        if _index_type is None:
            self.container.append(obj)
        else:
            self.container[_index_type] = obj
        _index = len(self.container) - 1 if _index_type is None else _index_type

        self.types[_type] = _index
        self.names[key] = _index

    def __getitem__(self, item):
        _index = self._get_index(item)
        return self.container[_index] if _index is not None else None

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise ValueError(f'Key {key} must be name of object. Not use type set item')
        self.put(value, key)

    def __len__(self):
        return len(self.container)

    def __iter__(self):
        for _type, _index in self.types.items():
            _obj = self.container[_index]
            _name = self.get_name_from_type(_type)
            yield _name, _type, _obj

    def __contains__(self, item):
        _index = self._get_index(item)
        return _index is not None

    def get_name_from_type(self, _type):
        _index = self._get_index(_type)
        _names = [k for k, v in self.names.items() if v == _index]
        if len(_names) != 1:
            raise ValueError('A collision occurred. The object has multiple names or the name was not found.')
        return _names[0]

    def _get_index(self, key):
        """
        Get index of object by type or name. For type registered subclasses will be used as well
        :param key: name or type
        :return:
        """
        if isinstance(key, str) and key in self.names.keys():
            return self.names[key]
        if isinstance(key, type):
            if key in self.types.keys():
                return self.types[key]
            else:
                # Find subclass
                _types = [v for k, v in self.types.items() if issubclass(k, key)]
                return _types[0] if len(_types) > 0 else None

        return None

    def _get_type_from_object(self, obj):
        return type(obj)
