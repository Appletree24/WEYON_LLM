from langchain_community.embeddings import XinferenceEmbeddings
from unittest import TestCase


class TestLocalEmbedding(TestCase):
    def test_xinference(self):
        xinference = XinferenceEmbeddings(
            server_url="http://192.168.100.111:9997",
            model_uid='bge-m3'
        )
        self.assertIsNotNone(xinference)
