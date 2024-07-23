#!//home/kemove/miniconda3/envs/llm/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Rag.py
# @Time      :2024/07/23 14:22:08
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 基于Llamaindex编写的Rag
# @Version   :1.0
# @Conda Env : llm
# 请不要用GPT生成代码中的注释，谢谢。

import logging
import sys
from llama_index.core import SimpleDirectoryReader, Settings, StorageContext, VectorStoreIndex, SimpleKeywordTableIndex
from llama_index.core.indices.query.query_transform import HyDEQueryTransform
from llama_index.core.indices.query.query_transform.base import StepDecomposeQueryTransform
from llama_index.core.query_engine import TransformQueryEngine
from llama_index.llms.openai_like import OpenAILike
from llama_index.core.postprocessor import MetadataReplacementPostProcessor, SentenceTransformerRerank
from llama_index.core.node_parser import SentenceWindowNodeParser, SentenceSplitter
from llama_index.core.query_engine import MultiStepQueryEngine
from llama_index.embeddings.langchain import LangchainEmbedding
from llama_index.vector_stores.qdrant import QdrantVectorStore
from langchain.embeddings.xinference import XinferenceEmbeddings
from langchain.retrievers.multi_query import MultiQueryRetriever
from langchain_openai import ChatOpenAI
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient, models

logging.basicConfig(stream=sys.stdout, level=logging.INFO)
logging.getLogger().addHandler(logging.StreamHandler(stream=sys.stdout))

langchain_embeddings = XinferenceEmbeddings(
    server_url="http://192.168.100.111:9997",
    model_uid="xiaobu-v2",
)

qdrant_clinet = QdrantClient(host="192.168.100.111", port=6333)

langchain_qdrant = Qdrant.from_existing_collection(
    embedding=langchain_embeddings,
    collection_name="Test_Llamaindex",
    location="http://192.168.100.111:6333",)

xinference_embeddings = LangchainEmbedding(
    langchain_embeddings=langchain_embeddings)

llm = OpenAILike(model="qwen2-pro", api_base="http://192.168.100.111:8001/v1",
                 api_key="apple", max_tokens=10000, temperature=0.5)

langchain_llm = ChatOpenAI(model="qwen2-pro", base_url="http://192.168.100.111:8001/v1",
                           api_key="tree", max_tokens=10000, temperature=0, max_retries=2, verbose=True, streaming=True)

node_parser = SentenceWindowNodeParser.from_defaults(
    window_size=3,
    window_metadata_key="window",
    original_text_metadata_key="original_text",
)

rerank = SentenceTransformerRerank(
    top_n=2,
    model="iampanda/zpoint_large_embedding_zh"
)

postproc = MetadataReplacementPostProcessor(
    target_metadata_key="window"
)

Settings.embed_model = xinference_embeddings
Settings.llm = llm
Settings.chunk_size = 1024
Settings.text_splitter = SentenceSplitter()

documents = SimpleDirectoryReader(
    input_dir="WEYON_LLM/resources/data/pdf").load_data(show_progress=True)

nodes = Settings.node_parser.get_nodes_from_documents(documents=documents)

vector_store = QdrantVectorStore(
    collection_name="Test_Llamaindex",
    client=qdrant_clinet,
    enable_hybrid=True,
    batch_size=20,
)

storage_context = StorageContext.from_defaults(vector_store=vector_store)
storage_context.docstore.add_documents(nodes)

vector_store_index = VectorStoreIndex.from_vector_store(
    vector_store=vector_store,
)

# NOTE alpha = 1为纯矢量搜索 0为纯关键字搜索
query_engine = vector_store_index.as_query_engine(
    llm=llm,
    similarity_top_k=2,
    sparse_top_k=12,
    vector_store_query_mode="hybrid",
    alpha=0.5,
    node_postprocessors=[rerank, postproc]
)

# TODO 
# Query Translation

# Multi-Step Query Engine



#multi_step_retriever = MultiQueryRetriever.from_llm(
#    retriever=langchain_qdrant.as_retriever(),
#    llm=langchain_llm,
#)
#
#unique_docs = multi_step_retriever.invoke("What is FLARE Query Engine?")
#
#print(unique_docs)


# HyDE (此方法不一定好，因为有可能生成引导错误的信息)
# hyde = HyDEQueryTransform(include_original=True)
# hyde_query_engine = TransformQueryEngine(
#    query_engine=query_engine, query_transform=hyde)
# response = hyde_query_engine.query("什么是FLARE Query Engine?")
# print(str(response))


# keyword_index = SimpleKeywordTableIndex(
#    nodes=nodes,
#    storage_context=storage_context,
# )
