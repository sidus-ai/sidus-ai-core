import inspect
from typing import Hashable

from sidusai.core.types import NamedTypedContainer

from sidusai.core.utils import camel_to_snake

__return__ = 'return'


def build_handler_name(handler):
    """
    Default handler string name
    :param handler:
    :return:
    """
    name = None
    if inspect.isclass(handler) or inspect.isfunction(handler):
        name = handler.__name__

    if inspect.ismethod(handler):
        name = handler.__qualname__

    if name is not None:
        name = camel_to_snake(name)

    return name


class Executable(Hashable):
    """
    Class-wrapper for wrap executable methods
    """

    def __init__(self, handler, order: int = 0):
        if not callable(handler):
            raise SyntaxError(f'Handler {handler} in Executable must be callable')

        self.handler = handler

        _params = inspect.getfullargspec(handler).annotations

        if not inspect.isclass(handler) \
                and not inspect.isfunction(handler) \
                and not inspect.ismethod(handler) \
                and callable(handler):
            _params = inspect.getfullargspec(handler.__call__).annotations

        if inspect.isclass(handler):
            self.return_param = handler
        else:
            self.return_param = _params[__return__] \
                if __return__ in _params and _params[__return__] is not None else None

        self.parameters = {k: v for k, v in _params.items() if k != __return__}
        self.default_name = build_handler_name(handler)
        self.order = order

    def __hash__(self):
        return hash(self)


class ExecutableContainer(NamedTypedContainer):
    """
    Container containing indexed executable methods
    """

    def _get_type_from_object(self, obj):
        if isinstance(obj, Executable):
            return obj.return_param

        raise TypeError('This container must be contains only Executable objects')


def build_parameters(executable: Executable, container: NamedTypedContainer):
    """
    Build  method arguments for executable object
    :param executable:
    :param container:
    :return:
    """
    args = {}
    for k, v in executable.parameters.items():
        if v == any:
            args[k] = container[k] if k in container else None
        else:
            args[k] = container[v] if v in container else None

    return args


def update_parameters_from_dict(args: dict, executable: Executable, container: dict):
    """
    Update the argument dictionary with an additional context parameter dictionary
    :param args:
    :param executable:
    :param container:
    :return:
    """
    typed_container = {type(v): v for k, v in container.items()}

    for k, v in executable.parameters.items():
        if k in container.keys():
            args[k] = container[k]
            continue
        for t in typed_container:
            if t == v or issubclass(v, t):
                args[k] = typed_container[v]


def execute_executable(executable: Executable, container: NamedTypedContainer, additional_container: dict = None):
    """
    Execute an executable object by generating method arguments from the container
    :param additional_container:
    :param container:
    :param executable: Executable object
    :return:
    """

    _args = build_parameters(executable, container)
    if additional_container is not None:
        update_parameters_from_dict(_args, executable, additional_container)
    _args = inspect.signature(executable.handler).bind(**_args).arguments
    return executable.handler(**_args)
