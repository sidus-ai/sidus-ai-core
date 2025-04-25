import re
import time
import importlib.util


def camel_to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def current_sec():
    return round(time.time())


def validate_modules(module_names: list):
    for name in module_names:
        if importlib.util.find_spec(name) is None:
            raise ModuleNotFoundError(
                f'Module {name} is not install. '
                f'Module required {name} module. Please install module'
            )
