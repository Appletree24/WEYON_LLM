"""
启动入口
"""
from langchain_core.runnables import Runnable

import logs
from agent.fay_agent import FayAgentCore
from chains import simple_chain
from basic import default_context

_ = simple_chain


def chain(message, history):
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


def rag(message, history):
    chain: Runnable = default_context['simple_rag']
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
    prompt = chain.invoke([message, history_msg])
    return str(prompt)


agent = FayAgentCore()


def simple_agent(message, history):
    user_input = message
    return agent.run(user_input)


import gradio as gr

if __name__ == "__main__":
    chain_interface = gr.ChatInterface(chain, title="Chain")
    rag_interface = gr.ChatInterface(rag, title="Rag")
    agent_interface = gr.ChatInterface(simple_agent, title="Agent")
    from fastapi import FastAPI

    app = FastAPI()
    gr.mount_gradio_app(app, chain_interface, path="/chain")
    gr.mount_gradio_app(app, agent_interface, path="/agent")
    gr.mount_gradio_app(app, rag_interface, path="/rag")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
