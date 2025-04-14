# SidusAI Framework
<sup>version 0.0.1 alpha</sup>

Imagine a tool that not only shoulders your daily burden but also unlocks horizons of infinite possibilities!
We create a lightweight and intuitive product that can become your trusty companion in the quest to conquer the tech
world. This power tool lets developers tailor its functionalities to their unique set of needs, scaling it infinitely.

Whether you need a web service, a background process, or a simple script, our tool is ready to be your reliable
assistant for any task. It performs its job with flawless precision and completes the process to a T, leaving you
with one crucial task - savoring the perfect result!

Join us on this exciting journey and explore new horizons in development! Your ideas deserve the best
realization - give them wings with our tool and watch them soar!

## About

Intense development unfolds in the field of artificial intelligence and AI agents. Over the past two years, our team
has actively researched and developed AI technologies and neural networks, applying them in various fields and
experimenting with practical aspects.

As a result, we have gained significant experience and created an extensive database that includes gigabytes of source
code. By combining this knowledge and development, we are pleased to present to you an innovative tool designed to
simplify the process of creating artificial intelligence agents.

This tool is a universal and easily scalable core system that allows developers to create AI agents quickly and
efficiently. We have gathered commonly used methods, functions, skills, and tasks to provide developers with a
powerful and flexible tool for building AI agents.

We believe that the integration of artificial intelligence agents into everyday life will be a true breakthrough.
These technologies will allow us to work more efficiently, create innovative products, and make our lives more
convenient. This, in turn, will open new horizons for achieving goals, gaining knowledge, and creating new inventions.

Our system is characterized by a high degree of flexibility and scalability. You can create your own tasks, events,
skills, actions, and integrations using a simple and fast plugin system that integrates with the core of the system.

The central core of the system is a multithreaded IoC container that manages the application lifecycle and maintains
the context of the current application: components, handlers, skills, and a weighted skill graph for solving
user tasks.

This approach to forming the task graph for the artificial intelligence agent provides the ability to determine which
skills are necessary for effectively solving specific tasks. It allows for real-time and uniquely tailored adaptation
of various skills of the AI agent to meet user needs.

Core elements such as connectors, handlers, processors, and pre-prepared skills are positioned above the core system
as plugins. This not only simplifies their use but also provides the opportunity to combine them for solving
diverse tasks.

These elements, interacting with each other and integrating into the core system, allow for the creation of unique
agents, much like how we build with LEGO bricks. The process is fast and easy, with limitations defined solely by
the developer of the specific agent.

## Use cases

1. Chatbot
2. Autonomous agents
3. Business process management
4. Characters for video games
5. Trade and financial services
6. Medical apps
7. Transport and logistics
8. Education
9. Entertainment
10. Smart devices and a Smart home

And many other areas of our lives

## Get started

To start using the SidusAI framework, simply follow the steps:
1. Install it using your package manager.
    ```commandline
    pip install git+https://github.com/sidus-ai/sidus-ai-core.git
    ```

2. Add the framework to your project's dependencies.

    ```python
    import sidusai as sai
    ```

3. Now you will be able to import the appropriate plugin or use a clean implementation of agents.
4. You can describe your task or use ready-made implementations of connectors, tasks, and skills.

    ```python
    import sidusai.plugins.deepseek as ds
    import sidusai.plugins.telegram as tg
    import sidusai.plugins.twitter as tw
    ```

5. Once you run the agent, you will get a solution to your task.

The code provided below demonstrates how easily and quickly agents can be assembled.
You can explore more complex agents in the [samples](https://github.com/sidus-ai/sidus-ai-core/tree/master/samples).

```python
import sidusai as sai
import sidusai.plugins.deepseek as ds

agent = ds.DeepSeekSingleChatAgent(
    api_key='<your deepseek api key>',
    system_prompt='<your system prompt>',
)


def accept_response(value: sai.ChatAgentValue):
    message = value.last_content()
    print(f'Assistant: {message}')


if __name__ == '__main__':
    agent.application_build()
    agent.send_to_chat(
        message='<your question>',
        handler=accept_response
    )
```

## Roadmap

We are actively improving our system by carefully analyzing and systematizing the accumulated experience and knowledge.
Our goal is to make the framework more user-friendly and functional. Currently, we only have an alpha version that
consolidates our achievements. However, there are still many tasks ahead that require solutions. In the near future,
we plan to implement the following items:

### Stage 1

- [X] IoC container for the core system
- [X]  Weighted graph of problem solving skills
- [X] Integrated plugin system
- [X] Integration of DeepSeek language models
- [ ] Integration of OpenAI language models
- [ ] Integration of pre-trained transformer language models, including Llama, Grok, Anthropic, Gemini, etc.
- [ ] Integration of custom models
- [X] Connector for Telegram
- [X] Connector for Twitter
- [ ] Connector for Discord
- [ ] Connectors for vector databases
- [ ] Connectors for databases

Undoubtedly, we will make every effort to keep this list up to date. However, the process of knowledge formation and
systematization is dynamic, which leads to a high speed and frequency of updates to the list.

## License

    Copyright 2025 SidusAI

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.

