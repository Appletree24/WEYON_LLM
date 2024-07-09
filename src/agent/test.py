# # from langchain_chroma import Chroma
# # from langchain_community.document_loaders import TextLoader
# from langchain_community.embeddings.sentence_transformer import (
#     SentenceTransformerEmbeddings,
# )
#
# # from langchain_text_splitters import CharacterTextSplitter
# #
# # loader = TextLoader("nihao.txt", encoding="UTF-8")
# # documents = loader.load()
# #
# # text_sqliter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# # docs = text_sqliter.split_documents(documents)
# #
# embedding_function = SentenceTransformerEmbeddings(model_name="all-MiniLM-L6-v2")
# #
# # db = Chroma.from_documents(docs, embedding_function)
# #
# # query = "长沙市"
# # docs = db.similarity_search(query, k=1)
# #
# # print(docs[0].page_content)
# import ast
# import re
#
# import os
# from langchain.chains.sql_database.query import create_sql_query_chain
# from langchain_community.utilities import SQLDatabase
# from langchain_community.vectorstores import FAISS
# from langchain_openai import OpenAIEmbeddings
# from operator import itemgetter
#
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_core.runnables import RunnablePassthrough
# from langchain_openai import ChatOpenAI
# import utils.config_util as utils
#
# db_user = "root"
# db_password = "AI20240520"
# db_host = "192.168.100.111"
# db_name = "ai_use"
# db_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
# db = SQLDatabase.from_uri(db_uri)
#
# utils.load_config()
# os.environ["OPENAI_API_KEY"] = utils.key_gpt_api_key
# os.environ["OPENAI_API_BASE"] = utils.gpt_base_url
# # 创建llm
# llm = ChatOpenAI(model=utils.gpt_model_engine)
#
#
# # vector_db = FAISS.from_texts(proper_nouns, embedding_function)
# # retriever = vector_db.as_retriever(search_kwargs={"k": 1})
# #
# # system = """You are a SQLite expert. Given an input question, create a syntactically
# # correct SQLite query to run. Unless otherwise specificed, do not return more than
# # {top_k} rows.
# #
# # Answer the question MUST based on the following context
# # Only return the SQL query with no markup or explanation.
# #
# # Here is the relevant table info: {table_info}
# #
# # Here is a non-exhaustive list of possible feature values. If filtering on a feature
# # value make sure to check its spelling against this list first:
# #
# # {proper_nouns}
# # """
# #
# # # 希望输入管家此{top_k} {table_info} {proper_nouns}
# # prompt = ChatPromptTemplate.from_messages([("system", system), ("human", "{input}")])
# #
# # query_chain = create_sql_query_chain(llm, db, prompt=prompt)
# # retriever_chain = (
# #         itemgetter("question")
# #         | retriever
# #         | (lambda docs: "\n".join(doc.page_content for doc in docs))
# # )
# # chain = RunnablePassthrough.assign(proper_nouns=retriever_chain) | query_chain
# # query = query_chain.invoke(
# #     {"question": "铲杀市 的 云酒业大学 2021届学生的就业数据", "proper_nouns": ""}
# # )
# # print(query)
# # db.run(query)
# import json
# from pathlib import Path
# from pprint import pprint
# from langchain_community.document_loaders import JSONLoader
# from langchain_openai import OpenAIEmbeddings
# from langchain_qdrant import Qdrant
# from langchain_text_splitters import CharacterTextSplitter
# from langchain_core.documents import Document
#
# file_path = 'nihao.json'
# data = json.loads(Path(file_path).read_text(encoding='UTF-8'))
# document = []
# for key, value in data.items():
#     document.append(
#         Document(
#             page_content=,
#             metadata=key
#         )
#     )
#
# print(document)
# text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=0)
# docs = text_splitter.split_documents(document)
# embeddings = embedding_function
#
# qdrant = Qdrant.from_documents(
#     docs,
#     embeddings,
#     location=":memory:",  # Local mode with in-memory storage only
#     collection_name="my_documents",
# )
#
# # url = "<---qdrant url here --->"
# # url = "http://localhost:6333"
# # qdrant = Qdrant.from_documents(
# #     docs,
# #     embeddings,
# #     url=url,
# #     prefer_grpc=True,
# #     collection_name="my_documents",
# #     force_recreate=True,
# # )
#
# query = "有哪些城市"
# found_docs = qdrant.similarity_search(query)
# print(found_docs[0].page_content)

# -*- coding:utf-8 -*-

import time
time1 = time.time()

# DFA算法
class DFAFilter():
    def __init__(self):
        self.keyword_chains = {}
        self.delimit = '\x00'

    def add(self, keyword):
        keyword = keyword.lower()
        chars = keyword.strip()
        if not chars:
            return
        level = self.keyword_chains
        for i in range(len(chars)):
            if chars[i] in level:
                level = level[chars[i]]
            else:
                if not isinstance(level, dict):
                    break
                for j in range(i, len(chars)):
                    level[chars[j]] = {}
                    last_level, last_char = level, chars[j]
                    level = level[chars[j]]
                last_level[last_char] = {self.delimit: 0}
                break
        if i == len(chars) - 1:
            level[self.delimit] = 0

    def parse(self, path):
        with open(path, encoding='utf-8') as f:
            for keyword in f:
                self.add(str(keyword).strip())

    def filter(self, message, replacements):
        message = message.lower()
        ret = []
        start = 0
        while start < len(message):
            level = self.keyword_chains
            step_ins = 0
            found = False
            for char in message[start:]:
                if char in level:
                    step_ins += 1
                    if self.delimit not in level[char]:
                        level = level[char]
                    else:
                        found = True
                        original_term = message[start:start+step_ins]
                        replacement_term = replacements.get(original_term, original_term)
                        ret.append(replacement_term)
                        start += step_ins - 1
                        break
                else:
                    break
            if not found:
                ret.append(message[start])
            start += 1
        return ''.join(ret)


if __name__ == "__main__":
    gfw = DFAFilter()

    # 添加替换词语
    replacements = {
        '湖南': '湖南省',
        '垫子商务专业': '电子商务专业'
    }

    # 可以通过文件添加敏感词
    # path = "F:/文本反垃圾算法/sensitive_words.txt"
    # gfw.parse(path)

    # 也可以直接在代码中添加敏感词
    gfw.add('湖南')
    gfw.add('垫子商务专业')

    text = "我是一个湖南人，我现在很想知道湖南一些大学的毕业生数据，因为我孩子明年想在湖南读大学"
    result = gfw.filter(text, replacements)

    print(text)
    print(result)
    time2 = time.time()
    print('总共耗时：' + str(time2 - time1) + 's')
