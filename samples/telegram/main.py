import os
import sidusai.plugins.deepseek as ds
import sidusai.plugins.telegram as tg

bot_api_key = os.environ.get('TG_API_KEY')
deepseek_api_key = os.environ.get('DEEPSEEK_API_KEY')

system_prompt = 'You are a very helpful assistant. You answer briefly.'

deepseek_plugin = ds.DeepSeekPlugin(
    api_key=deepseek_api_key
)

agent = tg.TelegramAiAgent(
    bot_api_key=bot_api_key,
    system_prompt=system_prompt,
    plugins=[deepseek_plugin],
)


@agent.bot.message_handler(content_types=['text'])
def tg_handler(message):
    tg_request = tg.TelegramRequest(message)
    agent.send_answer(tg_request)


if __name__ == '__main__':
    agent.application_run()
