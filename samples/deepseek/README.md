### DeepSeek integration sample

This is an example of integration with the Deep Seek language model. It uses auxiliary plug-ins 
that extend the agent's capabilities by adding a standard interaction task, to which skills are 
applied that implement message processing using a language model.

You can add your own agent skills to  prepare the message, if required.

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight. 
For plugins to work, you need to install dependencies in your project yourself.

```requirements
requests==2.32.3
```

Please use this commandline for install dependencies:

```commandline
pip install requests
```

### Environments

To set up and run the example, use the following environment variables. They are necessary for 
proper connection to external suppliers/consumers.

```properties
DEEPSEEK_API_KEY=xx-XXXXXXXXXXXXXXXXXXXXXXXXXX
```