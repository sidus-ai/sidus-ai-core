from sidusai.core.agent import Agent
from sidusai.core.types import AgentTask, AgentValue

import sidusai.core.execute as ex


class AgentPlugin:
    """
    An abstract wrapper class for a system plugin that extends the basic core
    with specific functionality to solve problems.
    """

    def __init__(self):
        pass

    def apply_plugin(self, agent: Agent):
        """
        Use this method to register the plugin's components, skills, tasks, and configurations.
        This will allow the plugin to integrate into the core infrastructure.
        :param agent: The agent object that the plugin integrates into
        """
        pass


class SampleConnectionPlugin(AgentPlugin):
    """
    The basic  plugin wrapper used for to connect to external data sources or provider services.
    """

    def __init__(self):
        super().__init__()


class SampleAiPlugin(AgentPlugin):
    """
    The basic  plugin wrapper used for to connect to
    external AI services with api or use local models (customs too).
    """

    def __init__(self):
        super().__init__()


class SampleBootPlugin(AgentPlugin):
    """
    The basic infrastructure plugin used for the configuration of the end application
    """

    def __init__(self):
        super().__init__()


class StringAgentValue(AgentValue):
    """
    The base agent data type is a data wrapper for a string value that is used to
    transform text in a chain of transformations.

    The class is basic and can be extended for custom implementations.
    """

    def __init__(self, value: str):
        super().__init__()
        self.value = value


class ChatAgentValue(AgentValue):
    """
    The agent's base data type, which wraps an array of user and agent message objects.

    Most often, such an agent is transformed by adding a new element to the array
    describing the user's or agent's message. The logic can be overridden by the user.
    """

    messages: list = []

    def __init__(self, messages):
        super().__init__()
        self.messages = messages

    def last_content(self) -> str | None:
        if len(self.messages) > 0:
            message = self.messages[-1:][0]
            return message['content'] if 'content' in message else None
        return None

    def append_user(self, content: str):
        self._append('user', content)

    def append_assistant(self, content: str):
        self._append('assistant', content)

    def append_system(self, content: str):
        self._append('system', content)

    def _append(self, role: str, content: str):
        self.messages.append({'role': role, 'content': content})


class CompletedAgentTask(AgentTask):
    """
    This is auxiliary class-extension for creating general-purpose tasks
    An object constructor that generates data transformation tasks and
    passes call completion to a higher level.
    """

    def __init__(self, agent: Agent, value: AgentValue | None = None, handler=None):
        super().__init__()

        self.value = value
        self.ctx = agent.ctx
        self.handler = self._build_executable_handler(handler)

    def data(self, value: AgentValue):
        self.value = value
        return self

    def then(self, handler):
        self.handler = self._build_executable_handler(handler)
        return self

    def forward(self, *args, **kwargs) -> AgentValue:
        return self.value

    def on_complete(self, value: AgentValue, *args, **kwargs) -> None:
        if self.handler is not None:
            ex.execute_executable(self.handler, self.ctx.components, {'value': value})

    @staticmethod
    def _build_executable_handler(handler) -> ex.Executable | None:
        _ex = None
        if handler is not None:
            _ex = ex.Executable(handler)

        return _ex


#################################################################
# Utility methods
#################################################################

def build_and_register_task_skill_names(task_skills: list, agent: Agent):
    """
    An additional method used in the plugins that allows you to apply a skill group
    to the agent context and get a list of registered skill names. For registered skills,
    its current name will be obtained.
    The resulting list can contain both the methods themselves,
    then they will be registered as skills, as well as the names of already registered skills.

    :param task_skills: A list of skills. Names or objects of functions
    :param agent: The current agent's object
    :return: Current list of registered skills
    """
    skill_names = []
    for task_skill in task_skills:
        # If it is name of skill
        if type(task_skill) is str:
            skill_names.append(task_skill)
            continue

        skill = agent.ctx.get_skill_by_handler(task_skill)
        if skill is None:
            # Add skill, if not exist
            new_skill = agent.ctx.add_agent_skill(task_skill)
            skill_names.append(new_skill.name)
        else:
            skill_names.append(skill.name)
    return skill_names
