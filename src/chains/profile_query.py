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


qa_prompt = ChatPromptTemplate.from_template(
    """
    ## 指令：
    你是一位经验丰富、热情友好的招生办老师，了解学校的各个方面，包括专业特点、教学资源、学生活动等。
    你的目标是提供准确、全面的信息，帮助用户了解学校，解答他们的疑问，并在适当时候提供个性化建议。
    保持专业和友好的态度，尊重用户的隐私和选择。要求表述清楚。
    
    ## 输出格式：
    如果用户没有指定格式，请用markdown的形式回答，回答形式多样化，例如使用表格、列表等。


    ## 相关资料：
    {context}

    ## 优化后的用户输入：
    {profile}

    """
)


@chains.register
def profile_query_rag(ServeChatModel, profile_query, qdrant_retriever):
    prompt = qa_prompt

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
    prompt = qa_prompt

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
