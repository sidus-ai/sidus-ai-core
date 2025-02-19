# This is an example of using application context.
#
# This script has one task with two skills and two user dependencies. One of which demonstrates
# the operation of configuration components, and the second one acts as a data processing service.
#
# Also, for the sake of example, one configuration is implemented, fine-tuning the components,
# as well as a post-processor method, which is supposed to perform the role of the final
# configuration of the component after applying all available configurations.
#


import datetime

import sidusai

# Create agent
agent = sidusai.Agent()


# Sample data class
class SampleValue(sidusai.AgentValue):
    """
    Example data class from receptor
    """

    def __init__(self, value: int):
        super().__init__()

        self.value = value


# Sample configuration property component
@agent.component()
class SampleApplicationProperties:
    def __init__(self):
        self.origin = 100


# Sample service component
@agent.component()
class SampleMathComponent:
    def __init__(self):
        print('Create sample math service')
        self.first_skill_dist = 0
        self.second_skill_dist = 0

    def add_first(self, value):
        return value + self.first_skill_dist

    def sub_second(self, value):
        return value - self.second_skill_dist


# First configuration for update component
@agent.configuration(order=0)
def sample_component_configuration(math_component: SampleMathComponent):
    math_component.first_skill_dist = 0
    math_component.second_skill_dist = 7


# Second configuration for update component
@agent.configuration(order=1)
def sample_component_configuration_second(math_component: SampleMathComponent):
    math_component.first_skill_dist = 4


# After all configuration methods have been completed
@agent.post_processor()
def sample_component_post_processor(math_component: SampleMathComponent):
    print(f'Add value: {math_component.first_skill_dist}')
    print(f'Sub value: {math_component.second_skill_dist}')


# Agent skill for add first value
@agent.skill()
def sample_skill_add_first(value: SampleValue, math: SampleMathComponent) -> SampleValue:
    value.value = math.add_first(value.value)
    return value


# Agent skill for sub second value
@agent.skill('sub_second')
def sample_skill_sub_second(value: SampleValue, math: SampleMathComponent) -> SampleValue:
    value.value = math.sub_second(value.value)
    return value


# Agent task
@agent.task(
    task_name='numeric_task',
    skill_names=['sample_skill_add_first', 'sub_second', 'sub_second'],
)
class NumericAgentTask(sidusai.AgentTask):
    def __init__(self, prop: SampleApplicationProperties):
        super().__init__()

        self.prop = prop
        print(f'Create new instance for Numeric task.')

    # Generate start value
    def forward(self) -> SampleValue:
        return SampleValue(self.prop.origin)

    # We get the value after using the agent's skills
    def on_complete(self, value: SampleValue, **kwargs) -> None:
        print(f'Complete task from {self.prop.origin} to {value.value}')

        self.prop.origin = value.value


# Injection into the main loop of the application, repeated every 10 seconds
@agent.loop(fixed_interval_sec=3)
def example_loop(prop: SampleApplicationProperties):
    if prop.origin <= 0:
        # Stopping the application programmatically
        agent.halt()

    dt = datetime.datetime.now()
    print(f'\nStart task at: {dt}')

    # Create and execute application
    task = agent.create_task_from_context(NumericAgentTask)
    agent.task_execute(task)


if __name__ == '__main__':
    # Start application
    agent.application_run()
