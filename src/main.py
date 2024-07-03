"""
启动入口
"""
import gradio as gr
from langchain_core.runnables import Runnable

import logs
from chains import simple_chain
from basic import default_context

_ = simple_chain


def simple_chain(message, history):
    chain: Runnable = default_context['simple_chain']
    partial_message = ""
    # 历史对话总是从用户开始，然后机器人
    history_msg = []
    for i, (user_message, bot_message) in enumerate(history):
        if isinstance(user_message, list):
            user_message = "".join(user_message)
        history_msg.append(('user', user_message))
        if isinstance(bot_message, list):
            bot_message = "".join(bot_message)
        history_msg.append(('ai', bot_message))
    history_msg = str(history_msg)
    logs.get_logger('chat').debug(history_msg)
    for chunk in chain.stream([message, history_msg]):
        partial_message = partial_message + chunk.content
        yield partial_message


if __name__ == "__main__":
    gr.ChatInterface(simple_chain).launch()
