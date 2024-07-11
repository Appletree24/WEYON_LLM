#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Rag.py
# @Time      :2024/07/11 11:47:47
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: Advanced-Rag
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from typing import List

from langchain.retrievers import ContextualCompressionRetriever
from langchain.retrievers import ParentDocumentRetriever
from langchain.retrievers.document_compressors.base import DocumentCompressorPipeline
from langchain.retrievers.document_compressors.chain_extract import LLMChainExtractor
from langchain.retrievers.document_compressors.embeddings_filter import EmbeddingsFilter
from langchain.storage import InMemoryStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_transformers import EmbeddingsRedundantFilter
# from qdrant_client.http.exceptions import UnexpectedResponse as NOTFOUND_COLLECTION
from langchain_community.document_transformers.long_context_reorder import LongContextReorder
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_core.retrievers import BaseRetriever
from langchain_openai import ChatOpenAI
from langchain_qdrant import Qdrant
from qdrant_client import QdrantClient, models

from utils.Files_util import get_docxs_without_splitter


# ATTENTION 如果按照之前的策略，一个用户给一个Collection，那Collection中的Points数量会不断增加，如何解决？
# 并且如果一个Collection里放很多文档，有没有必要做Merger了？那不一个Retriever就解决了？
# SOLVE 目前的解决方案是一个Retriever，但是绝对是不可靠的，需要进一步解决


class RagMain():
    model_name: str = ""
    embedding_name: str = ""
    llm: ChatOpenAI = None
    file_loaders: List[Docx2txtLoader] = None
    embeddings_gte = HuggingFaceEmbeddings(model_name="thenlper/gte-large")
    embeddings_bge = HuggingFaceEmbeddings(model_name='BAAI/bge-m3')
    embeddings_jina = HuggingFaceEmbeddings(
        model_name="jinaai/jina-embeddings-v2-base-zh")
    parent_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=64,
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
            "",
        ])
    child_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=64,
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
            "",
        ])

    qdrant_client = QdrantClient(location="192.168.100.111:6333")
    docs_store = InMemoryStore()

    retriever: BaseRetriever

    def __init__(self, model_name: str, openai_api_key: str, openai_api_base: str,
                 max_tokens: int, verbose: bool, collection_name: str, files_path: str) -> None:
        self.llm = ChatOpenAI(model=model_name, max_tokens=max_tokens, max_retries=2,
                              api_key=openai_api_key, base_url=openai_api_base, streaming=True,
                              verbose=verbose)
        if files_path == "":
            raise ValueError("files_path is Empty")
        if self.qdrant_client.collection_exists(collection_name=collection_name) is False:
            self.qdrant_client.create_collection(
                collection_name=collection_name,
                vectors_config=models.VectorParams(
                    size=1024,
                    distance=models.Distance.COSINE
                )
            )
        qdrant_child = Qdrant(
            self.qdrant_client,
            collection_name=collection_name,
            embeddings=self.embeddings_bge
        )
        parent_retriever = ParentDocumentRetriever(
            parent_splitter=self.parent_splitter,
            child_splitter=self.child_splitter,
            vectorstore=qdrant_child,
            docstore=self.docs_store,
        )

        docxs = get_docxs_without_splitter(files_path=files_path)

        parent_retriever.add_documents(docxs)

        redundant_filter = EmbeddingsRedundantFilter(
            embeddings=self.embeddings_jina)

        relevant_filter = EmbeddingsFilter(
            embeddings=self.embeddings_jina, k=5)

        reorder = LongContextReorder()

        compressor = LLMChainExtractor.from_llm(self.llm)

        pipeline = DocumentCompressorPipeline(
            transformers=[compressor, redundant_filter,
                          relevant_filter, reorder]
        )

        self.retriever = ContextualCompressionRetriever(
            base_retriever=parent_retriever,
            base_compressor=pipeline
        )

        print("Rag初始化完成")
