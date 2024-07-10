#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :LIM_rag.py
# @Time      :2024/07/08 16:44:34
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: Prevent LIM Pipeline
# @From : https://arxiv.org/abs//2307.03172
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

# TODO 取舍Cluster or redundant

# llamaindex version : https://www.llamaindex.ai/blog/longllmlingua-bye-bye-to-middle-loss-and-save-on-your-rag-costs-via-prompt-compression-54b559b9ddf7

# ATTENTION
# 创建不同的VectorStore，使用MergerRetriever
# 使用LongContextReorder重排序避免性能下降

# MergerRetriever以列表形式输入多个Retriever，将多个结果合并
# MergerRetriever可以对不同的Retriever进行排序，确保返回最相关的文档

import chromadb.config
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.document_transformers.long_context_reorder import LongContextReorder
from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_transformers.embeddings_redundant_filter import EmbeddingsClusteringFilter
from langchain.retrievers.contextual_compression import ContextualCompressionRetriever
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.retrievers.document_compressors.base import DocumentCompressorPipeline
from langchain.retrievers import MergerRetriever
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.chains.retrieval_qa.base import RetrievalQA

llm = ChatOpenAI(model="qwen2-pro", max_tokens=5000, max_retries=2, api_key="dummy",
                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True)

# ATTENTION 给chroma设置这个会报错，暂时可以搁置，因为用qdrant
# ABS_PATH = os.path.dirname(os.path.abspath(__file__))
# DB_DIR = os.path.join(ABS_PATH, "db")
#
# client_settings = chromadb.config.Settings(
#    is_persistent=True,
#    persist_directory=DB_DIR,
#    anonymized_telemetry=False,
# )

embeddings_name = "thenlper/gte-large"

embeddings_hf = HuggingFaceEmbeddings(model_name=embeddings_name)
embeddings_bge = HuggingFaceEmbeddings(model_name='BAAI/bge-m3')
embeddings_jina = HuggingFaceEmbeddings(
    model_name="jinaai/jina-embeddings-v2-base-zh")

pdf_loader = PyPDFLoader(
    file_path='WEYON_LLM/RAG/Study_abroad.pdf')
pdf_file = pdf_loader.load()
pdf_file_2 = PyPDFLoader(
    file_path='WEYON_LLM/RAG/Party.pdf').load()
print(f"文档1大小为{len(pdf_file)}")
print(f"文档2大小为{len(pdf_file_2)}")

chinese_text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64, separators=[
    "\n\n",
    "\n",
    " ",
    ".",
    ",",
    "\u200B",  # 零宽度空格
    "\uff0c",  # 全角逗号
    "\u3001",  # 顿号
    "\uff0e",  # 全角句号
    "\u3002",  # 句号
    "",
])

chunks_abroad = chinese_text_splitter.split_documents(pdf_file)
chunks_party = chinese_text_splitter.split_documents(pdf_file_2)
print(f"文档1分块大小为{len(chunks_abroad)}")
print(f"文档2分块大小为{len(chunks_party)}")

abroad_vectoreStore = Chroma.from_documents(
    documents=chunks_abroad,
    embedding=embeddings_hf,
    collection_name="study_abroad",
    collection_metadata={"hnsw": "cosine"},
    persist_directory='db/store/abroad'
)

party_vectoreStore = Chroma.from_documents(
    documents=chunks_party,
    embedding=embeddings_bge,
    collection_name="party",
    collection_metadata={"hnsw": "cosine"},
    persist_directory='db/store/party'
)

abroad_retriever = abroad_vectoreStore.as_retriever(
    search_kwargs={"k": 5}
)

party_retriever = party_vectoreStore.as_retriever(
    search_kwargs={"k": 5}
)

# NOTE
# EmsembleRetriever和MergerRetriever都可以组合多个Triever的结果，但策略不同
# EmsembleRetriver使用倒数排名融合（Reciprocal Rank Fusion）,使用检索器列表和相应的权重列表作为输入，如果没有手动提供权重，则默认全部权重相同
# 每份文件的计算方式为：权重乘以(排名的倒数加上常数C)
# https://learn.microsoft.com/zh-cn/azure/search/hybrid-search-ranking

# MergerRetriever使用循环方式合并不同triever的输出。
# Lord of the Retrievers（LOTR）又称 MergerRetriever，它将检索器列表作为输入，并将其 get_relevant_documents() 方法的结果合并为一个列表。 合并后的结果将是与查询相关的文档列表，这些文档已被不同的检索器排序。
# ATTENTION 合并很可能会有冗余的内容，这就要引入之前的EmbeddingsRedundantFilter借助其他embeddings来删除
# Langchain同样提供了使用聚类算法的过滤器，例如EmbeddingsClusterFilter，选择距离中心document最近的文档作为过滤结果

lotr = MergerRetriever(retrievers=[abroad_retriever, party_retriever])


# filter_ordered_by_retriever = EmbeddingsClusteringFilter(
#    embeddings=embeddings_jina,
#    num_clusters=10,
#    num_closest=1,
#    sorted=True,
# )

filter = EmbeddingsRedundantFilter(embeddings=embeddings_jina)

# ATTENTION 重排好像有点问题，根据arxiv论文中的内容，模型会在文档数大于10时出现显著的性能下降
# 但如果文档数较少，重排的效果好像不如不重排……

reorder = LongContextReorder()

pipeline = DocumentCompressorPipeline(
    transformers=[filter, reorder]
)

compression_retriever_reordered = ContextualCompressionRetriever(
    base_retriever=lotr,
    base_compressor=pipeline,
    search_kwargs={"k": 5}
)

qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=compression_retriever_reordered,
)

print(qa_chain.invoke({"query": "xxx2024年9月-2025年1月会在什么地方？"}))
