"""
启动入口
"""
from langchain_core.runnables import Runnable
from starlette.staticfiles import StaticFiles

import logs
from agent.fay_agent import FayAgentCore
from basic import default_context
from chains import simple_chain, profile_query

_ = simple_chain, profile_query


def history_chat_build(history):
    # 历史对话总是从用户开始，然后机器人
    history_msg = []
    history = history[-default_context['remember_history']:]
    for i, (user_message, bot_message) in enumerate(history):
        if isinstance(user_message, list):
            user_message = "".join(user_message)
        history_msg.append(('user', user_message))
        if isinstance(bot_message, list):
            bot_message = "".join(bot_message)
        history_msg.append(('ai', bot_message))
    history_msg = str(history_msg).replace(r"\n", "\n")
    return history_msg


def profile_rag_msg(message, history):
    history_msg = history_chat_build(history)
    pro_chain: Runnable = default_context['profile_query']
    res = pro_chain.invoke({'chat_history': history_msg, 'question': message})
    if res['stop']:
        yield res['profile'] + "🥰"
    else:
        partial_message = ""
        if res['keywords']:
            tips = f"> 🤔 关键词 : **{res['keywords']}**\n\n"
            partial_message += tips
            yield partial_message
        retriever_chain: Runnable = default_context['retriever_chain']

        for chunk in retriever_chain.stream(res):
            partial_message += chunk.content
            yield partial_message
        yield partial_message + "🥰"


def profile_rag(message, history):
    chain: Runnable = default_context['profile_query_rag']
    history_msg = history_chat_build(history)
    partial_message = ""
    logs.get_logger('chat').debug(history_msg)
    for chunk in chain.stream({"question": message, "chat_history": history_msg}):
        partial_message = partial_message + chunk.content
        yield partial_message
    yield partial_message + "🥰"


def simple_rag(message, history):
    chain: Runnable = default_context['simple_chain']
    # 历史对话总是从用户开始，然后机器人
    history_msg = history_chat_build(history)
    partial_message = ""
    logs.get_logger('chat').debug(history_msg)
    for chunk in chain.stream([message, history_msg]):
        partial_message = partial_message + chunk.content
        yield partial_message
    yield partial_message + "🥰"


def simple_chat(message, history):
    chain: Runnable = default_context['ServeChatModel']
    # 历史对话总是从用户开始，然后机器人
    history_msg = history_chat_build(history)
    partial_message = ""
    logs.get_logger('chat').debug(history_msg)
    for chunk in chain.stream([history_msg, message]):
        partial_message = partial_message + chunk.content
        yield partial_message


agent = FayAgentCore()


def simple_agent(message, history):
    user_input = message
    return agent.run(user_input, agent.qdrant_retriever)[1]


def retriever_test(message, history):
    retriever = default_context['DocRetriever']
    re = retriever.invoke(message)
    if len(re) > 0:
        res = '\n\n---\n\n## '.join([doc.page_content for doc in re])
    else:
        return "# 🥹 未找到相关内容"
    msg = f'# 🥰【{message}】的检索结果\n\n##' + res
    return msg


# 公司名称
company_name = "WeYon"
con_limit = 20

import gradio as gr

config = {
    "theme": "soft",
    "submit_btn": "发送",
    "retry_btn": "重试",
    "undo_btn": "撤回并重新编辑",
    "clear_btn": "新建对话",
    "stop_btn": "停止",
    "chatbot": gr.Chatbot(placeholder="Powered By WeYon AI Department", likeable=True, label="Chatbot", scale=1,
                          height=200),
    "textbox": gr.Textbox(placeholder="与WeYon AI对话", scale=8),
}

if __name__ == "__main__":
    rag_interface = gr.ChatInterface(simple_rag, title=f"{company_name} Question Rag", concurrency_limit=con_limit,
                                     description=f"{company_name} 基于问题检索对话",
                                     **config)
    profile_interface = gr.ChatInterface(profile_rag_msg, title=f"{company_name} Keywords Rag",
                                         concurrency_limit=con_limit,
                                         description=f"{company_name} 基于关键词检索",
                                         **config
                                         )
    chat_interface = gr.ChatInterface(simple_chat, title=f"{company_name} Chat", concurrency_limit=con_limit,
                                      description=f"{company_name} 直接与模型对话",
                                      **config)
    agent_interface = gr.ChatInterface(simple_agent, title=f"{company_name} Agent", concurrency_limit=con_limit,
                                       description=f"{company_name} 查询数据库的智能体",
                                       **config)
    retriever_test_interface = gr.ChatInterface(fn=retriever_test,
                                                title=f"{company_name} Retriever命中率测试",
                                                description="用来测试Retriever命中率，生产环境记得关闭！！当前测试对象为DocRetriever",
                                                **config)

    from fastapi import FastAPI

    app = FastAPI()
    gr.mount_gradio_app(app, rag_interface, path="/rag")
    gr.mount_gradio_app(app, profile_interface, path="/profile/")
    gr.mount_gradio_app(app, chat_interface, path="/chat")
    gr.mount_gradio_app(app, agent_interface, path="/agent")
    gr.mount_gradio_app(app, retriever_test_interface, path="/retriever")

    app.mount("/", StaticFiles(directory="./pages", html=True), name="pages")

    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
