"""
用来优化用户查询的链
"""
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableLambda

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
        可以适当的联想和扩充，但一定要符合原文主旨。你可以正确的关联的历史对话，从历史对话中提取出有用的信息辅助回答问题。
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

    def extra_keywords(p):
        res = {}

        def extra_with(li, start):
            return [i for i in li if i.strip().startswith(start)]

        pros = p.content.splitlines()
        res['profile'] = p.content
        res['keywords'] = extra_with(pros, '关键词：')
        res['extra_keywords'] = extra_with(pros, '联想关键词：')
        res['profile_query'] = extra_with(pros, '优化后的输入：')
        return res

    profile_query_chain = (prompt
                           | RunnableLambda(log)
                           | ServeChatModel
                           | RunnableLambda(extra_keywords))
    return profile_query_chain


@chains.register
def profile_query_rag(ServeChatModel, profile_query, qdrant_retriever):
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
        res = p.copy()
        # 仅用关键词从向量数据库中查询数据
        res['context'] = qdrant_retriever.invoke(str(p['extra_keywords']))
        return res

    return (profile_query | RunnableLambda(retriever) |
            RunnableLambda(log) | prompt | ServeChatModel)


@chains.register
def retriever_chain(ServeChatModel, qdrant_retriever):
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
        res = p.copy()
        # 仅用关键词从向量数据库中查询数据
        res['context'] = qdrant_retriever.invoke(str(p['extra_keywords']))
        return res

    return (RunnableLambda(retriever) |
            RunnableLambda(log) | prompt | ServeChatModel)
