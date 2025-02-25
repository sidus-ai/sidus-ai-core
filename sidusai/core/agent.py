import inspect
import threading as th
import time

import sidusai.core.context as context
import sidusai.core.execute as ex
import sidusai.core.types as types
import sidusai.core.utils as utils

__default_agent_name__ = '_default_agent_name_'


class Agent:
    """
    Default wrap application life cycle
    """

    def __init__(self, agent_name: str = __default_agent_name__):
        self.agent_name = agent_name
        self.ctx = context.AgentContext(self.agent_name)
        self.is_builded = False
        self.is_enabled = True

    #################################################################
    # Core decorators
    #################################################################

    def component(self, name: str = None):
        """
        Injectable to context services.
        This is a special class or method builder that initializes the singleton component,
        available for use as part of the agent's execution of its tasks.
        :return:
        """

        def decorator(handler):
            self.add_component_builder(builder=handler, name=name)
            return handler

        return decorator

    def skill(self, name: str = None):
        """
        Decorator for create application skill.
        This is a special class or method for forming the logic of an agent's available action.
        :param name:
        :return:
        """

        def decorator(handler):
            self.add_skill(handler, name)
            return handler

        return decorator

    def task(self, task_name: str, skill_names: [str] = None):
        """
        Decorator for create user's task
        This is a special class for forming and describing the logic of the task being solved by the agent.
        :return:
        """

        def decorator(handler):
            self.task_registration(handler=handler, name=task_name, skill_names=skill_names)
            return handler

        return decorator

    def configuration(self, order: int = 0):
        """
        Decorator for create user's configurations method

        Configuration is performed after components are created in the context and before
        skills and the main application loop are generated.
        :return:
        """

        def decorator(handler):
            self.add_configuration(handler, order)
            return handler

        return decorator

    def post_processor(self, order: int = 0):
        """
        Decorator for create user's post-processors methods
        The post processor is used to assemble components after they have been fine-tuned into a configuration.
        :return:
        """

        def decorator(handler):
            self.add_post_processor(handler, order)
            return handler

        return decorator

    def loop(self, fixed_interval_sec: int = None, order: int = 0):
        """
        Decorator for life cycle methods
        :param fixed_interval_sec:
        :param order:
        :return:
        """

        def decorator(handler):
            self.add_loop_method(handler, fixed_interval_sec, order)
            return handler

        return decorator

    #################################################################
    # Configuration context method
    #################################################################

    def add_component_builder(self, builder, name: str = None):
        """
        Add component builder (factory or factory method) to context
        :param builder:
        :param name:
        :return:
        """
        if not inspect.isfunction(builder) and not inspect.isclass(builder) and not inspect.ismethod(builder):
            raise ValueError(f'Invalid service. Service \'{builder}\' must be class or function')
        self.ctx.add_component_builder(builder, name=name)

    def add_skill(self, handler, name: str = None):
        """
        Add skill method/class to context
        :param handler: Function/Method/class skill.
        :param name: Skill name
        :return:
        """
        self.ctx.add_agent_skill(skill=handler, skill_name=name)

    def task_registration(self, handler, name: str = None, skill_names: [str] = None):
        """
        Registration task type to context.
        :param skill_names:
        :param handler:
        :param name:
        :return:
        """
        self.ctx.add_task_class(handler, name, skill_names)

    def add_configuration(self, handler, order: int = 0):
        """
        Add configuration method to context.
        :param order:
        :param handler:
        :return:
        """
        self.ctx.add_configuration_handler(handler, order)

    def add_post_processor(self, handler, order: int = 0):
        """
        Add component post processor (use in configuration component)
        :param order:
        :param handler:
        :return:
        """
        self.ctx.add_post_processor(handler, order)

    def add_loop_method(self, handler, fixed_interval_sec: int = 0, order: int = 0):
        """
        Add custom loop method to life cycle context
        :param handler:
        :param fixed_interval_sec:
        :param order:
        :return:
        """
        self.ctx.add_loop_method(handler, fixed_interval_sec, order)

    #################################################################
    # Application
    #################################################################

    def create_task_from_context(self, task: str | type):
        """
        Create a task object instance using the current context
        To create a task, use registered task types or names.
        :param task: str or type
        :return:
        """
        return context.make_task(task, self.ctx)

    def task_execute(self, task: types.AgentTask):
        """
        Performing a task using active skills in a separate thread
        :param task:
        :return:
        """
        _thread = th.Thread(target=context.task_execute, args=(task, self.ctx,))
        _thread.start()

    def application_build(self):
        if self.is_builded:
            raise EnvironmentError('Context already build.')

        # Build context (run all builders)

        #  Build and create all single-ton components
        context.build_components(self.ctx)
        # Component configuration
        context.sort_executables_by_order(self.ctx.configurations)
        context.sort_executables_by_order(self.ctx.post_processors)
        context.executable_list(self.ctx.configurations, self.ctx)
        context.executable_list(self.ctx.post_processors, self.ctx)

        # Build and storage all skills
        context.build_skills(self.ctx)
        context.validate_skills(self.ctx)

        # Build tasks
        context.build_tasks(self.ctx)

        self.is_builded = True

    def application_run(self, interval: int = 1):
        """
        Implementation of the main loop of the application. As long as the active flag is set,
        the application is executed, launching the corresponding annotated methods as needed at
        a given interval in separate threads
        :param interval: wait between iterations
        :return:
        """
        if not self.is_builded:
            self.application_build()
        while self.is_enabled:
            cur_ms = utils.current_sec()
            for loop in self.ctx.loops:
                if loop.fixed_interval_sec is not None and cur_ms - loop.last_loop_at > loop.fixed_interval_sec and not loop.is_executing:
                    loop.is_executing = True
                    thread_name = f'thread_{loop.executable.default_name}'
                    # TODO: Create a queue pool to limit the number of tasks running in parallel
                    _thread = th.Thread(target=self._execute_loop, name=thread_name, args=(loop,))
                    _thread.start()
            time.sleep(interval)

    def _execute_loop(self, loop):
        ex.execute_executable(loop.executable, self.ctx.components)
        loop.is_executing = False
        loop.last_loop_at = utils.current_sec()

    def halt(self):
        self.is_enabled = False


class AgentExtension:
    """
    Agent extension class.
    Used to implement user and system extensions.
    """

    def __init__(self, agent: Agent):
        self.agent = agent
