"""
启动入口
"""
import gradio as gr
from langchain_core.runnables import Runnable

import logs
from agent.fay_agent import FayAgentCore
from chains import simple_chain, advanced_chain
from basic import default_context

_ = simple_chain, advanced_chain


def advanced_retriever(message, history):
    advanced_chain_test: Runnable = default_context['advanced_chain'] 
    #chain: Runnable = default_context['advanced_chain']
    #partial_message = ""
    ## 历史对话总是从用户开始，然后机器人
    #history_msg = []
    #for i, (user_message, bot_message) in enumerate(history[-4:]):
    #    if isinstance(user_message, list):
    #        user_message = "".join(user_message)
    #    history_msg.append(('user', user_message))
    #    if isinstance(bot_message, list):
    #        bot_message = "".join(bot_message)
    #    history_msg.append(('ai', bot_message))
    #history_msg = str(history_msg).replace(r"\n", "\n")
    #logs.get_logger('chat').debug(history_msg)
    #for chunk in chain.stream([message, history_msg]):
    #    partial_message = partial_message + chunk.content
    #    yield partial_message
    return advanced_chain_test.invoke({"query": message})['result']
    # for chunk in chain.invoke({"query": message}):
    #    partial_message = partial_message + chunk['result']
    #    yield partial_message


def chain(message, history):
    chain: Runnable = default_context['simple_chain']
    partial_message = ""
    # 历史对话总是从用户开始，然后机器人
    history_msg = []
    for i, (user_message, bot_message) in enumerate(history[-4:]):
        if isinstance(user_message, list):
            user_message = "".join(user_message)
        history_msg.append(('user', user_message))
        if isinstance(bot_message, list):
            bot_message = "".join(bot_message)
        history_msg.append(('ai', bot_message))
    history_msg = str(history_msg).replace(r"\n", "\n")
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
    return agent.run(user_input, agent.qdrant_retriever)[1]


if __name__ == "__main__":
    chain_interface = gr.ChatInterface(chain, title="Simple Chain")
    rag_interface = gr.ChatInterface(rag, title="Simple Rag")
    agent_interface = gr.ChatInterface(simple_agent, title="Simple Agent")
    advanced_chain_interface = gr.ChatInterface(
        advanced_retriever, title="Simple Retriever")
    from fastapi import FastAPI

    app = FastAPI()
    gr.mount_gradio_app(app, chain_interface, path="/chain")
    gr.mount_gradio_app(app, agent_interface, path="/agent")
    gr.mount_gradio_app(app, rag_interface, path="/rag")
    gr.mount_gradio_app(app, advanced_chain_interface, path="/advanced_chain")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
