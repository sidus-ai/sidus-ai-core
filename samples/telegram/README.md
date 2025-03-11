### Telegram Bot integration sample

A simple implementation of a telegram bot. The bot forward the user's messages into requests to the 
language model of the DeepSeek plugin. The response of the language model is sent to the users. 
In the example, several simultaneous requests are blocked. The bot saves the context of up to 
100 messages in RAM

### Dependencies

The default kernel does not contain the dependencies required for plugins, as it is lightweight. 
For plugins to work, you need to install dependencies in your project yourself.

```requirements
pyTelegramBotAPI==4.26.0
requests==2.32.3
```

Please use this commandline for install dependencies:

```commandline
pip install pyTelegramBotAPI requests
```


### Environments

To set up and run the example, use the following environment variables. They are necessary for proper 
connection to external suppliers/consumers.

```properties
TG_API_KEY=000000000:XXXXXXXXXXXXXXXXXXXXXXXXXXXX
DEEPSEEK_API_KEY=xx-XXXXXXXXXXXXXXXXXXXXXXXXXX
```