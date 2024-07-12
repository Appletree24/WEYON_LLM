"""
用来优化用户查询的链
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough

import chains
from llm import chat_openai
from logs import get_logger
from retriever import qdrant_retriever

_ = chat_openai, qdrant_retriever

sys_prompt = ""
logger = get_logger('profile_query')


@chains.register
def profile_query(ServeChatModel):
    prompt = ChatPromptTemplate.from_template(
        """
        ## 指令：
        请优化用户的输入，简称变成正式的全称，错别字修正。将优化后的结果输出。然后提取其中的关键词。
        可以适当的联想和扩充，但一定要符合原文主旨。你可以正确的关联以有的历史对话。
        当理解上出现模棱两可时，尽可能向教育、大学、职业发展规划等方向倾斜。

        ## 格式： 
        优化后的输入：XXX。
        ---
        关键词：XXX 
        ---
        联想关键词： XXX
        ---
        历史对话或者上下文的参考：XXX

        ## 历史对话：
        {chat_history}
        
        ## 用户输入         ：
        {question}

        """
    )

    def log(p):
        logger.debug(p)
        return p

    profile_query_chain = (prompt
                           | RunnableLambda(log)
                           | ServeChatModel)
    return profile_query_chain


@chains.register
def profile_query_chain(ServeChatModel, profile_query, qdrant_retriever):
    prompt = ChatPromptTemplate.from_template(
        """
        ## 指令：
        你是一位湘潭大学招生办的老师，你的任务是尽你所能回答学生或者家长的问题。下面是用户的问题以及我帮你整理好的相关资料。可以用作参考。
        请一定要符合事实。联想词可以用来参考，但是一定以关键词为主。尽量简明的给出答案，分点作答。
        
        ## 相关资料：
        {context}
        
        ## 优化后的用户输入：
        {profile}
        
        """
    )

    def log(p):
        logger.debug(p)
        return p

    def retriever(p):
        res = {'profile': p['profile'].content}
        res['context'] = qdrant_retriever.invoke(res['profile'])
        return res

    # TODO 抽取关键词，从retriever中查找相关文档
    return ({'profile': profile_query} | RunnableLambda(retriever) |
            RunnableLambda(log) | prompt | ServeChatModel)
