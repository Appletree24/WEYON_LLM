#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Qdrant_Vector_Store.py
# @Time      :2024/07/16 09:56:31
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: Llamaindex中的Qdrant
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。
import logging
import sys

import qdrant_client
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import StorageContext
from llama_index.vector_stores.qdrant import QdrantVectorStore
from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.embeddings.fastembed import FastEmbedEmbedding
from llama_index.core.schema import TextNode
from llama_index.core import Settings, ServiceContext
from llama_index.llms.openai_like import OpenAILike
from llama_index.core import Document, set_global_service_context
from llama_index.core.base.llms.types import ChatMessage, MessageRole
from llama_index.core.vector_stores import MetadataFilter, MetadataFilters, FilterOperator, FilterCondition

llm = OpenAILike(model="qwen2-pro", api_base="http://192.168.100.111:8000/v1",
                 api_key="dummy", max_tokens=5000)

embed_model = FastEmbedEmbedding(model_name="BAAI/bge-small-zh-v1.5")


service_context = ServiceContext.from_defaults(
    embed_model=embed_model, llm=llm)

set_global_service_context(service_context)


logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

client = qdrant_client.QdrantClient(
    location=":memory:"
)

nodes = [
    TextNode(
        text="The Shawshank Redemption",
        metadata={
            "author": "Stephen King",
            "theme": "Friendship",
            "year": 1994,
        },
    ),
    TextNode(
        text="The Godfather",
        metadata={
            "director": "Francis Ford Coppola",
            "theme": "Mafia",
            "year": 1972,
        },
    ),
    TextNode(
        text="Inception",
        metadata={
            "director": "Christopher Nolan",
            "theme": "Fiction",
            "year": 2010,
        },
    ),
    TextNode(
        text="To Kill a Mockingbird",
        metadata={
            "author": "Harper Lee",
            "theme": "Mafia",
            "year": 1960,
        },
    ),
    TextNode(
        text="1984",
        metadata={
            "author": "George Orwell",
            "theme": "Totalitarianism",
            "year": 1949,
        },
    ),
    TextNode(
        text="The Great Gatsby",
        metadata={
            "author": "F. Scott Fitzgerald",
            "theme": "The American Dream",
            "year": 1925,
        },
    ),
    TextNode(
        text="Harry Potter and the Sorcerer's Stone",
        metadata={
            "author": "J.K. Rowling",
            "theme": "Fiction",
            "year": 1997,
        },
    ),
]

vector_store = QdrantVectorStore(
    client=client, collection_name="test_llama"
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)
index = VectorStoreIndex(nodes, storage_context=storage_context)

filters = MetadataFilters(
    filters=[
        MetadataFilter(key="theme", operator=FilterOperator.EQ,
                       value="Fiction"),
        MetadataFilter(key="year", operator=FilterOperator.GT, value=1997)
    ],
    condition=FilterCondition.AND,
)

retriever = index.as_retriever(filters=filters)

response = retriever.retrieve("Harry Potter?")

print(response)


# documents = SimpleDirectoryReader(
#    input_dir='WEYON_LLM/resources/data').load_data()
#
# client = qdrant_client.QdrantClient(host="192.168.100.111", port=6333)
#
# vector_store = QdrantVectorStore(
#    client=client, collection_name="test_LlamaIndex")
#
# storage_context = StorageContext.from_defaults(vector_store=vector_store)
#
# index = VectorStoreIndex.from_documents(
#    documents,
#    storage_context=storage_context,
# )
#
# qdrant_triever = index.as_retriever(similarity_top_k=5)
#
# query_engine = RetrieverQueryEngine.from_args(
#    retriever=qdrant_triever
# )
#
# response = query_engine.retrieve("谁的孩子被摔死了?")
#
# answer = llm.chat(
#    messages=[
#        ChatMessage(role=MessageRole.SYSTEM,
#                    content="你是一个精通西游记故事的大师，我会给你西游记的上下文，请你回答问题并提供相关联想知识"),
#        ChatMessage(role=MessageRole.USER,
#                    content=response[0].text+"谁的孩子被摔死了?")
#    ]
# )
#
# print(str(answer))
