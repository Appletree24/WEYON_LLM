from unittest import TestCase

from langchain_community.embeddings import XinferenceEmbeddings


class TestLocalEmbedding(TestCase):
    def test_xinference(self):
        xinference = XinferenceEmbeddings(
            server_url="http://192.168.100.111:9997",
            model_uid='bge-m3'
        )
        self.assertIsNotNone(xinference)
