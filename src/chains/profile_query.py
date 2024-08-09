"""
用来优化用户查询的链
"""
import langchain.prompts
from langchain_core.runnables import RunnableLambda

import chains
from chains.common import global_data
from llm import chat_openai
from logs import get_logger
from retriever import qdrant_retriever, doc_retriever

_ = chat_openai, qdrant_retriever, doc_retriever

logger = get_logger('profile_query')


def log(p):
    logger.debug(p)
    return p


def extra_keywords(p):
    res = {}

    def extra_with(li, start):
        return [i for i in li if i.strip().startswith(start)]

    res['stop'] = '我无法理解您的意思' in p.content
    pros = p.content.splitlines()
    res['profile'] = pros
    res['keywords'] = extra_with(pros, '关键词：')
    res['extra_keywords'] = extra_with(pros, '联想关键词：')
    res['profile_query'] = extra_with(pros, '优化后的输入：')
    return res


@chains.register
def profile_query(ServeChatModel, profile_query_prompt):
    prompt = langchain.prompts.load_prompt(profile_query_prompt['path'])
    profile_query_chain = (global_data
                           | prompt
                           | RunnableLambda(log)
                           | ServeChatModel
                           | RunnableLambda(extra_keywords))
    return profile_query_chain


@chains.register
def profile_query_rag(ServeChatModel, profile_query, DocRetriever, profiled_query_prompt):
    prompt = langchain.prompts.load_prompt(profiled_query_prompt['path'])

    def retriever(p):
        res = p.copy()
        # 仅用关键词从向量数据库中查询数据
        res['context'] = DocRetriever.invoke(str(p['keywords']))
        return res

    return (global_data
            | profile_query
            | RunnableLambda(retriever)
            | global_data
            | RunnableLambda(log)
            | prompt
            | ServeChatModel)


@chains.register
def retriever_chain(ServeChatModel, DocRetriever, profiled_query_prompt):
    prompt = langchain.prompts.load_prompt(profiled_query_prompt['path'])

    def retriever(p):
        res = p.copy()
        # 仅用关键词从向量数据库中查询数据
        res['context'] = DocRetriever.invoke(str(p['profile']))
        return res

    return (global_data
            | RunnableLambda(retriever)
            | RunnableLambda(log)
            | prompt
            | ServeChatModel)
