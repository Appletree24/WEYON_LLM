from unittest import TestCase
from embedding import modelscope_embedding
from vector_store import qdrant
from basic import default_context
from qdrant_client import QdrantClient


class TestQdrantVectorStore(TestCase):

    def test_qdrant_client(self):
        """测试qdrant客户端连接"""
        client: QdrantClient = default_context.get_bean('qdrant_client')
        res = client.get_collections()
        self.assertIsNotNone(res)

    def test_qdrant_vector_store(self):
        qdrant_vector_store: qdrant.QdrantVectorStore = default_context.get_bean('QdrantVectorStore')
        self.assertIsNotNone(qdrant_vector_store)
        # 测试向量存储
        res = qdrant_vector_store.similarity_search("llama")
        self.assertIsNotNone(res)