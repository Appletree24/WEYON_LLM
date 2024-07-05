#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Langchain_SQL_Agents.py
# @Time      :2024/07/05 14:30:15
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 利用Langchain框架编写的ReAct nl2SQL Agent
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

import os
import re
import ast
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.agents.agent_toolkits import create_retriever_tool
from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory.buffer import ConversationBufferMemory
from langchain_community.document_loaders.csv_loader import CSVLoader

os.environ["OPENAI_API_BASE"] = "http://192.168.100.111:9997/v1"
os.environ["OPENAI_API_KEY"] = "dummy"
os.environ["CUDA_VISIBLE_DEVICES"] = "1"


class PromptPrinter(BaseCallbackHandler):
    def on_llm_start(self, serialized, prompts, **kwargs):
        print(f"输入给LLM的Prompt为:{prompts[0]}")


class PromptCapturingHandler(BaseCallbackHandler):
    def __init__(self):
        self.llm_prompts = []

    def on_llm_end(self, serialized, prompts, **kwargs):
        self.llm_prompts.append(prompts)


embeeding_name = "thenlper/gte-large"
embeedings = HuggingFaceEmbeddings(model_name=embeeding_name)

loader = CSVLoader(file_path='WEYON_LLM/RAG/Text2SQL/Example_SQL.csv')

sample_sql = loader.load()

# print(sample_sql)

chinese_text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64, separators=[
    "\n\n",
    "\n",
    " ",
    ".",
    ",",
    "\u200B",  # Zero-width space
    "\uff0c",  # Fullwidth comma
    "\u3001",  # Ideographic comma
    "\uff0e",  # Fullwidth full stop
    "\u3002",  # Ideographic full stop
    "",
])

sql_example_chunks = chinese_text_splitter.split_documents(sample_sql)

# from langchain.agents.react.agent import create_react_agent


SQL_PREFIX = """You are an agent designed to interact with a SQL database.
Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
You can order the results by a relevant column to return the most interesting examples in the database.
Never query for all the columns from a specific table, only ask for the relevant columns given the question.
You have access to tools for interacting with the database.
Only use the below tools. Only use the information returned by the below tools to construct your final answer.
You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.

DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.

To start you should ALWAYS look at the tables in the database to see what you can query.
Do NOT skip this step.
Then you should query the schema of the most relevant tables."""


# system_message = SystemMessage(content=SQL_PREFIX)

db_user = "root"
db_password = "AI20240520"
db_host = "192.168.100.111"
db_name = "ai_use"


db_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

db = SQLDatabase.from_uri(db_uri)

# db = SQLDatabase.from_uri("sqlite:///WEYON_LLM/RAG/Text2SQL/Chinnok.db")

chinese_system_ = """
你是一个与 SQL 数据库交互的代理。
给定一个输入问题，创建一个语法正确的 SQLite 查询来运行，然后查看查询结果并返回答案。
除非用户指定了希望获得的示例的具体数量，否则始终将查询结果限制为最多 5 个。
您可以根据相关列对结果进行排序，以返回数据库中最有趣的示例。
切勿查询特定表中的所有列，只查询问题中的相关列。
您可以使用与数据库交互的工具。
只能使用指定的工具。只能使用工具返回的信息来构建您的最终答案。
执行查询前必须仔细检查。如果在执行查询时出现错误，请重写查询并再试一次。

切勿对数据库执行任何 DML 语句（INSERT、UPDATE、DELETE、DROP 等）。

您可以访问以下表：{table_names}

如果需要过滤专有名词，必须首先使用 "search_proper_nouns "工具查找过滤值！
不要试图猜测专有名词，而是使用该功能查找相似的专有名词。

""".format(table_names=db.get_usable_table_names())

chinese_system = chinese_system_ + "上下文对话历史为{chat_history}"


CUSTOM_SQL_QUESTION_PROMPT = PromptTemplate.from_template(chinese_system)

chat_memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)


# system = """You are an agent designed to interact with a SQL database.
# Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
# Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
# You can order the results by a relevant column to return the most interesting examples in the database.
# Never query for all the columns from a specific table, only ask for the relevant columns given the question.
# You have access to tools for interacting with the database.
# Only use the given tools. Only use the information returned by the tools to construct your final answer.
# You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
#
# DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
#
# You have access to the following tables: {table_names}
#
# If you need to filter on a proper noun, you must ALWAYS first look up the filter value using the "search_proper_nouns" tool!
# Do not try to guess at the proper name - use this function to find similar ones.""".format(
#    table_names=db.get_usable_table_names()
# )

llm = ChatOpenAI(model="qwen2", max_tokens=5000, max_retries=2)

toolkit = SQLDatabaseToolkit(db=db, llm=llm)

tools = toolkit.get_tools()

# agent_executor = create_react_agent(
#    model=llm, tools=tools, messages_modifier=system_message)

# for s in agent_executor.stream(
#    {"messages": [HumanMessage(content="Describe the dw_s_employment table")]}
# ):
#    print(s)
#    print("---------------------------------------------")


def query_as_list(db, query):
    res = db.run(query)
    res = [el for sub in ast.literal_eval(res) for el in sub if el]
    res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
    return list(set(res))


db = Chroma.from_documents(
    sql_example_chunks, embeedings, persist_directory="example_sql")

# prompt_capturing_handler = PromptCapturingHandler()


sql_qa_chain = ConversationalRetrievalChain.from_llm(
    llm=llm,
    memory=chat_memory,
    retriever=db.as_retriever(search_kwargs={"k": 3}),
    condense_question_prompt=CUSTOM_SQL_QUESTION_PROMPT,
    # callbacks=[prompt_capturing_handler]
    verbose=True
    # callbacks=[PromptPrinter()]
)


# ATTENTION 暂时废弃，目的是为了拿到RAG之后的输入，注册了回调发现无作用
# def get_rag_llm_input(query):
#    prompt_capturing_handler.llm_prompts.clear()
#    _ = sql_qa_chain({"question": query})
#    if prompt_capturing_handler.llm_prompts:
#        return prompt_capturing_handler.llm_prompts[-1]
#    return None


# query = "我该如何查询XX专业毕业生境内升学院校层次"
#
# result_ = sql_qa_chain({"question": query})
#
# result = result_["answer"].strip()
#
# print(result)
#

# unis = query_as_list(db, "SELECT zydl FROM dw_s_employment")


# _ = query_as_list(db, "SELECT Title FROM Album")

# vector_db = FAISS.from_texts(
#    unis, HuggingFaceEmbeddings(model_name="thenlper/gte-large"))

# vector_db = Chroma.from_texts(
#    unis, HuggingFaceEmbeddings(model_name="thenlper/gte-large"))
#
# retriever = vector_db.as_retriever(search_kwargs={"k": 3})
#
# description = """
# Use to look up values to filter on. Input is an approximate spelling of the proper noun, output is \
# valid proper nouns. Use the noun most similar to the search and replace the original wrong spelling.
# Such as: "search_proper_nouns('垫子商务')" to find the proper noun to filter on.
# Calling result will be '电子商务类'
# """
# retriever_tool = create_retriever_tool(
#    retriever=retriever,
#    name="search_proper nouns",
#    description=description
# )

# system_message = SystemMessage(content=system)

# tools.append(retriever_tool)

# agent = create_react_agent(llm, tools)
#
# for s in agent.stream(
#    {"messages": [HumanMessage(
#        content="查询10条来自云就业大学的学生就业数据")]}
# ):
#    print(s)
#    print("-----------------------------------------------")
#
