#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :rag_fusion.py
# @Time      :2024/07/12 17:24:37
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description:RAG中的Fusion模块
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from langchain.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain.load import dumps, loads
from langchain_chroma import Chroma
from langchain.document_loaders import Docx2txtLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from operator import itemgetter


def reciprocal_rank_fusion(results: list[list], k=60):
    fused_scores = {}

    for docs in results:
        for rank, doc in enumerate(docs):
            doc_str = dumps(doc)
            if doc_str not in fused_scores:
                fused_scores[doc_str] = 0
            fused_scores[doc_str] += 1 / (rank + k)

    reranked_results = [
        (loads(doc), score)
        for doc, score in sorted(fused_scores.items(), key=lambda x: x[1], reverse=True)
    ]

    return reranked_results


multi_template = """
你是一名人工智能语言模型助理。您的任务是生成四个给定用户问题的四个不同版本，以便从向量数据库中检索相关文档。通过对用户问题生成多种观点，你的目标是帮助用户克服基于距离的相似性搜索的一些局限性。

问题: {question}

输出(4 queries):
"""

template = """
根据下述上下文回答问题:

上下文:{context}

问题:{question}
"""

loader = Docx2txtLoader(file_path='WEYON_LLM/resources/doc/Chuanmei.docx')
doc_file = loader.load()

parent_splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=1024, chunk_overlap=50)

split_docs = parent_splitter.split_documents(doc_file)

vectorstore = Chroma.from_documents(
    split_docs, embedding=HuggingFaceEmbeddings(model_name="jinaai/jina-embeddings-v2-base-zh"))

retriever = vectorstore.as_retriever()


llm = ChatOpenAI(model='qwen2-pro', max_tokens=5000, max_retries=2, api_key="dummy",
                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True, temperature=0)

prompt_rag_fusion = ChatPromptTemplate.from_template(template=multi_template)

qa_prompt = ChatPromptTemplate.from_template(template=template)

generate_queries = (
    prompt_rag_fusion | llm | StrOutputParser() | (lambda x: x.split("\n"))
)

retrieval_chain_rag_fusion = generate_queries | retriever.map() | reciprocal_rank_fusion

qa_chain = (
    {"context": retrieval_chain_rag_fusion, "question": itemgetter(
        "question")} | qa_prompt | llm | StrOutputParser()
)

print(qa_chain.invoke({"question": "湖南大众传媒职业技术学院2023届毕业生的省内就业行业主要为?"}))
