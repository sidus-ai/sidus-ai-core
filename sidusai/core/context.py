import inspect

import sidusai.core.execute as ex
import sidusai.core.graph as graph
import sidusai.core.types as types


class AgentContext:
    """
    Default application context
    """

    def __init__(self, agent_name: str):
        if agent_name is None:
            raise ValueError('Agent name can not be None')
        self.agent_name = agent_name

        #############################################################
        # Builders and configurations
        #############################################################
        # Builders for singletons
        self.components_builders = ex.ExecutableContainer()

        # Post processors use in build method for configured components
        # after start application configuration
        self.post_processors = []

        # Methods (callable classes) use for configuration application and create new components
        self.configurations = []

        #############################################################
        # Application Context
        #############################################################

        # Application singletons
        self.components = types.NamedTypedContainer()

        #############################################################
        # Agent context
        #############################################################

        # Context skills
        self.skills = {}

        # Cache registered tasks
        #
        # The agent can only perform pre-registered tasks.
        # Since the tasks are targeted and pre-programmed,
        # the graph of their solution is formed at the program launch stage.
        # This way, heavy operations will be generated and cached in advance.
        self.tasks = {}

        # Reproducible Methods Registry Cache
        # The application's main loop runs methods on a schedule,
        # allowing events to be generated within the context.
        self.loops = []

        self.exception_handlers = []

    def get_skill_by_handler(self, handler) -> ex.Executable | None:
        for name, skill in self.skills.items():
            if skill.handler == handler:
                return skill
        return None

    def get_task_container(self, task_type: str | type) -> types.TaskContainer:
        _task = None
        for _name, _container in self.tasks.items():
            if _name == task_type or _container.task_type == task_type:
                _task = _container
                break
        return _task

    def get_exception_handlers(self, error_type: type) -> list:
        res = []
        for err in self.exception_handlers:
            if len(err.error_types) == 0 or error_type in err.error_types:
                res.append(err.executable)
                continue

            for _err_type in err.error_types:
                if issubclass(error_type, _err_type):
                    res.append(err.executable)
        return res

    def build_task(self, task_type: str | type):
        _task = self.get_task_container(task_type)
        if _task is None:
            raise ValueError(f'Task {task_type} is not found')

        return ex.execute_executable(_task.executable_init, self.components)

    def find_executable_skills(self, skill_names: list) -> list:
        return [self.skills[s] for s in skill_names]

    #############################################################
    # Configuration context
    #############################################################

    def add_component_builder(self, builder, name: str = None):
        """
        Add component builder method (or add component class) to context
        :param name:
        :param builder:
        :return:
        """
        executable = ex.Executable(handler=builder)
        if executable.return_param is None:
            raise ValueError(
                'The factory method of the service must explicitly specify the returned class type.'
            )
        _name = name if name is not None else executable.default_name

        if executable in self.components_builders or _name in self.components_builders:
            raise ValueError(f'Component {executable.handler} [{_name}] already exist')

        self.components_builders.put(executable, key=_name)

    def add_agent_skill(self, skill, skill_name: str = None) -> ex.Executable:
        """
        Method for adding a skill to the agent context.
        All agent skills will be initialized after the components are initialized.
        Components can be injected either into the class constructor or into the method parameters.
        :param skill: Function/Method/Class
        :param skill_name: User's skill name
        :return:
        """
        executable = ex.Executable(skill, name=skill_name)

        if executable.name in self.skills.keys():
            raise ValueError(
                f'Skill {executable.name} already exist. '
                'Avoid duplication in agent skill names. '
                'Duplication in names will lead to unpredictable collisions'
            )

        self.skills[executable.name] = executable
        return executable

    def add_task_class(self, handler, task_name: str, available_skills_names: list):
        """
        Register a task by configuring the task solution graph
        :param available_skills_names:
        :param handler:
        :param task_name:
        :return:
        """
        if not inspect.isclass(handler) or not issubclass(handler, types.AgentTask):
            raise SyntaxError(f'Task \'{handler}\' must be a class inherited from sai.Task')

        name = task_name if task_name is not None else ex.build_handler_name(handler)

        if name in self.tasks.keys():
            raise ValueError(f'Task {name} already exists')

        if available_skills_names is None or len(available_skills_names) == 0:
            raise ValueError(f'Task {name} have not skills')

        self.tasks[name] = types.TaskContainer(handler, task_name, available_skills_names)

    def add_post_processor(self, handler, order: int = 0):
        """
        Wrap and add to context component configuration post processor
        :param order:
        :param handler:
        :return:
        """
        if not callable(handler):
            raise ValueError(f'Post processor must be callable. {handler} is not a callable.')

        executable = ex.Executable(handler, order)
        self.post_processors.append(executable)

    def add_configuration_handler(self, handler, order: int = 0):
        """
        Wrap and add to context configuration method
        :param order:
        :param handler:
        :return:
        """
        if not callable(handler):
            raise ValueError(f'Configuration must be callable. {handler} is not a callable.')
        executable = ex.Executable(handler, order)
        self.configurations.append(executable)

    def add_loop_method(self, handler, fixed_interval_sec: int = None, order: int = 0):
        """

        :param order:
        :param handler:
        :param fixed_interval_sec:
        :return:
        """
        if not callable(handler):
            raise ValueError(f'Loop method must be callable. {handler} is not a callable.')

        if fixed_interval_sec is None:
            raise SyntaxError('Please use cron OR fixed interval')

        executable = ex.Executable(handler, order)
        container = types.LoopContainer(executable, fixed_interval_sec)
        self.loops.append(container)

    def add_exception_handler(self, handler, error_types: list = None, order: int = 0):
        if not callable(handler):
            raise ValueError(f'Exception handler {handler} mast be callable')

        executable = ex.Executable(handler, order)
        container = types.ExceptionHandlerContainer(executable, error_types)
        self.exception_handlers.append(container)


#############################################################
# Utility methods
#
# Methods of forming and filling context in runtime
#############################################################

def build_component_in_context(context: AgentContext, _type: type):
    """
    Create instance of component and save to context memory
    :param context: context
    :param _type:
    :return: component
    """
    builder = context.components_builders[_type]
    name = context.components_builders.get_name_from_type(_type)

    if builder is None:
        raise ValueError(f'Builder for component \'{_type}\' is not found.')

    component = context.components[_type]
    if component is not None:
        return component

    for k, v in builder.parameters.items():
        if v not in context.components:
            _ = build_component_in_context(context, v)

    component = ex.execute_executable(builder, context.components)
    context.components.put(component, name, _type)
    return component


def build_components(context: AgentContext):
    """
    Build components in context
    :param context:
    :return:
    """
    for _name, _type, _executable in context.components_builders:
        if _name in context.components or _type in context.components:
            # If this component already building
            continue
        _ = build_component_in_context(context, _type)


def build_skills(context: AgentContext):
    """
    For the skills defined by the class, we form singleton objects that implement the agent's skill
    :param context:
    :return:
    """
    _skills = {k: v for k, v in context.skills.items() if inspect.isclass(v.handler)}
    for skill_name, skill_class in _skills.items():
        handler = ex.execute_executable(skill_class, context.components)

        if not callable(handler):
            raise ValueError(
                f'Skill {skill_name} must be callable class. '
                'Please implement the __call()__ method.'
                'Specify in it additional arguments that should be injected from the context'
            )

        context.skills[skill_name] = ex.Executable(handler)


def validate_skills(context: AgentContext):
    """
    The method checks the correctness of the skill registration.
     All available skills must have a certain type.
    :param context:
    :return:
    """
    for skill_name, skill in context.skills.items():
        if skill.return_param is None:
            raise SyntaxError(
                f'Skill {skill_name} must have return value. '
                'The return data type must be explicitly specified. '
                'The data type must be inherited from the base data class sai.AgentValue'
            )

        parameters = [k for k, v in skill.parameters.items() if issubclass(v, types.AgentValue)]
        if len(parameters) != 1:
            raise SyntaxError(
                'The agent\'s skill works on the principle of transforming objects. '
                'For the skills to work correctly, it is necessary that the skills explicitly '
                'accept the object inherited from sai.AgentValue in a single copy.'
            )

    # skill is correct and can be use


def build_tasks(context: AgentContext):
    """

    :param context:
    :return:
    """
    for task_name, task_container in context.tasks.items():
        if not isinstance(task_container, types.TaskContainer):
            raise SyntaxError('Unexpected data type for task wrapper')
        task_container.executable_init = ex.Executable(task_container.task_type)
        task_container.skill_graph = build_skill_graph(task_container, context)


def build_skill_graph(
    task_container: types.TaskContainer,
    context: AgentContext
) -> graph.AgentSkillGraph:
    """
    Factory method for create graph
    :param task_container:
    :param context:
    :return:
    """
    full_skill_names = list(context.skills.keys())
    return graph.AgentSkillGraph(full_skill_names, task_container.available_skill_names)


def sort_executables_by_order(executables: list):
    """
    Sorting running objects by order key
    :param executables:
    :return:
    """
    executables.sort(key=lambda executable: executable.order)
