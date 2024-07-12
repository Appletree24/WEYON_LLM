from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

from RAG.rag_main import RagMain

import chains
from llm import chat_openai
from logs import get_logger

_ = chat_openai

sys_prompt = "你是一个拥有丰富知识的AI助手，能够充分利用上下文中的信息，来对用户提出的问题进行回答。回答请尽量简洁明确并分条表述，避免不需要的信息，也不要编造事实。"

logger = get_logger('simple_chain')


@chains.register
def advanced_chain(ServeChatModel):
    rag_main = RagMain(model_name="qwen2-pro",
                       openai_api_key="dummy",
                       openai_api_base="http://192.168.100.111:8000/v1",
                       max_tokens=10000,
                       verbose=True,
                       collection_name="test_1_1024",
                       files_path='/home/kemove/AI_Projects/zzh/WEYON_LLM/resources/doc')

    # prompt = ChatPromptTemplate.from_messages([
    #    ('system', sys_prompt),
    #    ('system', "今天是{date},星期{week}."),
    #    ('system', '目前已经发生的对话如下：{chat_history}'),
    #    ('system', '上下文：{context}'),
    #    ('system', '用户问题如下：'),
    #    ('user', '{question}')
    # ])

    # def log(p):
    #    logger.debug(p)
    #    return p

    # def tmp_get_config():
    #    return {"configurable": {"search_kwargs_qdrant": {"k": 3}}}

    # from datetime import datetime
    # advanced_chain = ({"date": RunnableLambda(lambda x: datetime.now().strftime("%Y年%m月%d日 %H:%M")),
    #                   "week": RunnableLambda(lambda x: datetime.now().strftime("%A"))}
    #                  | {"context": RunnableLambda(lambda x: rag_main.retriever.invoke(str(x), config=tmp_get_config())),
    #                     "question": RunnablePassthrough(lambda x: x[0]),
    #                     "chat_history": RunnablePassthrough(lambda x: x[1])}
    #                  | prompt
    #                  | RunnableLambda(log)
    #                  | ServeChatModel)
    return rag_main.qa_chain
