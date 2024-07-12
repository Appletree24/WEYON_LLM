#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :multi_query.py
# @Time      :2024/07/12 16:22:14
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: Rag中的Multi Query模块
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import WebBaseLoader
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.load import dumps, loads
from langchain.document_loaders import Docx2txtLoader
from operator import itemgetter


def get_unique_union(documents: list[list]):
    flattened_docs = [dumps(doc) for sublist in documents for doc in sublist]

    unique_docs = list(set(flattened_docs))

    return [loads(doc) for doc in unique_docs]


template = """
你是一名人工智能语言模型助理。您的任务是生成五个给定用户问题的五个不同版本，以便从向量数据库中检索相关文档。通过对用户问题生成多种观点，你的目标是帮助用户克服基于距离的相似性搜索的一些局限性。
你的目标是帮助用户克服基于距离的相似性搜索的一些局限性。
请提供这些用换行符分隔的备选问题。

原始问题: {question}
"""

query_template = """
依据下述上下文回答问题:

{context}

问题:{question}
"""

prompt = ChatPromptTemplate.from_template(template)

query_prompt = ChatPromptTemplate.from_template(query_template)

loader = Docx2txtLoader(file_path='WEYON_LLM/resources/doc/Chuanmei.docx')

# loader = WebBaseLoader(
#    web_path="https://baike.baidu.com/item/%E7%94%B5%E5%90%89%E4%BB%96/287117"
# )
llm = ChatOpenAI(model='qwen2-pro', max_tokens=5000, max_retries=2, api_key="dummy",
                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True)

web_docs = loader.load()

parent_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=300,
    chunk_overlap=50,
    separators=[
        "\n\n",
        "\n",
        " ",
        ".",
        ",",
        "\u200B",
        "\uff0c",
        "\u3001",
        "\uff0e",
        "\u3002",
        "",])

splits = parent_splitter.split_documents(web_docs)

vectorstore = Chroma.from_documents(
    documents=splits, embedding=HuggingFaceEmbeddings(model_name="BAAI/bge-m3"))

retriever = vectorstore.as_retriever()


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


rag_chain = (
    prompt | llm | StrOutputParser() | (lambda x: x.split("\n"))
)

retrieval_chain = rag_chain | retriever.map() | get_unique_union

qa_chain = (
    {"context": retrieval_chain, "question": itemgetter(
        "question")} | query_prompt | llm | StrOutputParser())

response = qa_chain.invoke(
    {"question": "湖南大众传媒职业技术学院2023届毕业生的省内就业行业主要为?"})
print(response)
