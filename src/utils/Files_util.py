#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Files_util.py
# @Time      :2024/07/11 14:05:11
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 文件操作工具类
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from langchain_community.document_loaders import Docx2txtLoader
from langchain_qdrant import Qdrant
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient, models
from langchain_core.embeddings import Embeddings
from langchain_community.document_loaders import DirectoryLoader


def create_upload_qdrant_collection(qdrant_clinet: QdrantClient,
                                    collection_name: str,
                                    files_path: str,
                                    embeddings: Embeddings,
                                    embeddings_dim: int,
                                    splitter: RecursiveCharacterTextSplitter) -> bool:
    if qdrant_clinet.collection_exists(collection_name=collection_name) is False:
        qdrant_clinet.create_collection(collection_name=collection_name,
                                        vectors_config=models.VectorParams(
                                            size=embeddings_dim,
                                            distance=models.Distance.COSINE
                                        ))
    if qdrant_clinet.get_collection(collection_name=collection_name).status == 'red':
        raise RuntimeError("Collection状态为red，无法上传数据")

    loader = DirectoryLoader(path=files_path,
                             glob="**/*.docx",
                             show_progress=True)
    docs = splitter.split_documents(loader.load())
    try:
        Qdrant.from_documents(
            docs,
            embeddings,
            location="192.168.100.111:6333",
            collection_name=collection_name
        )
        return True
    except Exception as e:
        print(e)
        return False


def upload_qdrant_collection(qdrant_clinet: QdrantClient,
                             collection_name: str,
                             files_path: str,
                             embeddings: Embeddings,
                             splitter: RecursiveCharacterTextSplitter):
    if qdrant_clinet.collection_exists(collection_name=collection_name) is False:
        raise ReferenceError(
            "该方法默认Collection存在，Collection不存在，请改用create_upload_qdrant_collection方法")

    if qdrant_clinet.get_collection(collection_name=collection_name).status == 'red':
        raise RuntimeError("Collection状态为red，无法上传数据")

    loader = DirectoryLoader(path=files_path,
                             glob="**/*.docx",
                             show_progress=True)
    docs = splitter.split_documents(loader.load())
    try:
        Qdrant.from_documents(
            docs,
            embeddings,
            location="192.168.100.111:6333",
            collection_name=collection_name
        )
    except Exception as e:
        raise e


def get_docxs_without_splitter(files_path: str):
    loader = DirectoryLoader(path=files_path,
                             glob="**/*.docx",
                             show_progress=True)
    return loader.load()
