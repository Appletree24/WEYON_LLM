from unittest import TestCase
from retriever import qdrant_retriever
from basic import default_context
from langchain_core.vectorstores import VectorStoreRetriever

_ = qdrant_retriever


class Test(TestCase):
    def test_qdrant_retriever(self):
        retriever: VectorStoreRetriever = default_context.get_bean("qdrant_retriever")
        res = retriever.invoke("hello")
        self.assertIsNotNone(res)
