from unittest import TestCase
from src.embedding import default_register


class TestModelScopeEmbeddings(TestCase):

    def test_embed_documents(self):
        embed = default_register.get_bean("ModelScopeEmbeddings")
        res = embed.embed_documents(["test"])
        print(res)

        self.assertEqual(len(res[0]), 768)

    def test_embed_query(self):
        embed = default_register.get_bean("ModelScopeEmbeddings")
        res = embed.embed_query("test")
        print(res)

        self.assertEqual(len(res), 768)
