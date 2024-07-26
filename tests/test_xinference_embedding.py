from unittest import TestCase

from basic import default_context
from embedding import xinference_embedding


class Test(TestCase):
    def test_xinference_embedding(self):
        embed: xinference_embedding.XinferenceEmbeddings = default_context['xinference_embedding']
        self.assertIsNotNone(embed)
        vector = embed.embed_query("wuhu")
        self.assertNotEqual(0, len(vector))
