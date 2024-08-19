from typing import List

from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever as LCBaseRetriever
from llama_index.core import QueryBundle
from llama_index.core.base.base_retriever import BaseRetriever as LIBaseRetriever
from llama_index.core.schema import NodeWithScore, TextNode
from qdrant_client.models import models

import retriever
from embedding import modelscope_embedding
from retriever.vector_store import qdrant

_ = modelscope_embedding, qdrant


class Config:
    metadata = 'metadata'
    parent_id = 'parent'
    order_by = 'idx'
    page_content = 'page_content'


@retriever.register
class DocRetriever(LCBaseRetriever):

    @staticmethod
    def merge_with_common_prefix(str1, str2):
        # 找到两个字符串的公共前缀
        common = ""
        for c1, c2 in zip(str1, str2):
            if c1 == c2:
                common += c1
            else:
                break
        # 合并字符串，只保留一份公共前缀
        merged = common + str1[len(common):] + '\n' + str2[len(common):]
        return merged

    QdrantVectorStore: qdrant.QdrantVectorStore
    retriever_config: dict

    @staticmethod
    def _remove_duplicates(lst):
        return list(set(lst))

    def _get_docs_by_parent(self, doc_rel: List[List[str]]) -> List[Document]:
        # langchain中的qdrant无法执行scroll操作，因此需要调用qdrant的python客户端
        collection_name = self.QdrantVectorStore.collection_name
        fil = models.Filter(
            should=[
                models.FieldCondition(key=f'{Config.metadata}.{Config.parent_id}', match=models.MatchAny(any=doc_rel))]
        )
        recs = self.QdrantVectorStore.client.scroll(collection_name=collection_name, scroll_filter=fil)
        return [Document(page_content=chunk.payload[Config.page_content], metadata=chunk.payload[Config.metadata]) for
                chunk in recs[0]]

    @staticmethod
    def _resort_doc(docs: List[Document]):
        docs.sort(key=lambda x: x.metadata[Config.order_by])

    def _merge_doc(self, docs: List[Document]) -> List[Document]:
        # 合并两个文档
        pre_doc: Document | None = None
        parent_id = None
        for doc in docs:
            if doc.metadata[Config.parent_id] != parent_id:
                parent_id = doc.metadata[Config.parent_id]
                pre_doc = doc
            else:
                pre_doc.page_content = self.merge_with_common_prefix(pre_doc.page_content, doc.page_content)
                doc.page_content = ""

        docs = [Document(page_content=doc.page_content) for doc in docs if doc.page_content != ""]
        return docs

    def __do_retriever(self, query: str):
        # LangChain的retriever
        chunks = self.QdrantVectorStore.similarity_search(query=query, **self.retriever_config)
        doc_rel = self._remove_duplicates(chunk.metadata.get(Config.parent_id) for chunk in chunks)
        docs = self._get_docs_by_parent(doc_rel)
        self._resort_doc(docs)
        docs = self._merge_doc(docs)
        return docs

    def _get_relevant_documents(self, query: str, *, run_manager: CallbackManagerForRetrieverRun) -> List[Document]:
        return self.__do_retriever(query)

    def as_llama_index_retriever(self):
        return LMRetriever(self)


class LMRetriever(LIBaseRetriever):
    def __init__(self, lc_retriever: DocRetriever):
        super().__init__()
        self.lc_retriever = lc_retriever

    def _retrieve(self, query_bundle: QueryBundle) -> List[NodeWithScore]:
        # LlamaIndex的retriever
        result = (self.lc_retriever.invoke(query_bundle.query_str))
        return [NodeWithScore(node=TextNode(text=res.page_content)) for res in result]
