"""
启动入口
"""
from langchain_core.runnables import Runnable

import logs
from basic import default_context
from chains import simple_chain, profile_query
from agent.fay_agent import FayAgentCore

_ = simple_chain, profile_query


def history_chat_build(history):
    # 历史对话总是从用户开始，然后机器人
    history_msg = []
    for i, (user_message, bot_message) in enumerate(history):
        if isinstance(user_message, list):
            user_message = "".join(user_message)
        history_msg.append(('user', user_message))
        if isinstance(bot_message, list):
            bot_message = "".join(bot_message)
        history_msg.append(('ai', bot_message))
    history_msg = str(history_msg).replace(r"\n", "\n")
    return history_msg


def profile_rag(message, history):
    chain: Runnable = default_context['profile_query_rag']
    history_msg = history_chat_build(history)
    partial_message = ""
    logs.get_logger('chat').debug(history_msg)
    for chunk in chain.stream({"question": message, "chat_history": history_msg}):
        partial_message = partial_message + chunk.content
        yield partial_message


def simple_rag(message, history):
    chain: Runnable = default_context['simple_chain']
    # 历史对话总是从用户开始，然后机器人
    history_msg = history_chat_build(history)
    partial_message = ""
    logs.get_logger('chat').debug(history_msg)
    for chunk in chain.stream([message, history_msg]):
        partial_message = partial_message + chunk.content
        yield partial_message


def simple_chat(message, history):
    chain: Runnable = default_context['ServeChatModel']
    # 历史对话总是从用户开始，然后机器人
    history_msg = history_chat_build(history)
    partial_message = ""
    logs.get_logger('chat').debug(history_msg)
    for chunk in chain.stream([message, history_msg]):
        partial_message = partial_message + chunk.content
        yield partial_message



agent = FayAgentCore()


def simple_agent(message, history):
    user_input = message
    return agent.run(user_input, agent.qdrant_retriever)[1]


# 公司名称
company_name = "WeYon"
con_limit = 20

import gradio as gr

if __name__ == "__main__":
    rag_interface = gr.ChatInterface(simple_rag, title=f"{company_name} Rag", concurrency_limit=con_limit)
    profile_interface = gr.ChatInterface(profile_rag, title=f"{company_name} Rag Pro", concurrency_limit=con_limit)
    chat_interface = gr.ChatInterface(simple_chat, title=f"{company_name} Chat", concurrency_limit=con_limit)
    agent_interface = gr.ChatInterface(simple_agent, title=f"{company_name} Chat", concurrency_limit=con_limit)
    from fastapi import FastAPI

    app = FastAPI()
    gr.mount_gradio_app(app, rag_interface, path="/rag")
    gr.mount_gradio_app(app, profile_interface, path="/rag/pro")
    gr.mount_gradio_app(app, chat_interface, path="/chat")
    gr.mount_gradio_app(app, agent_interface, path="/agent")
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
