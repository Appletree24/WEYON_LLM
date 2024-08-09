from unittest import TestCase

from basic import default_context
from retriever.doc_retriever import DocRetriever


class TestDocRetriever(TestCase):
    def test__get_relevant_documents(self):
        doc_retriever: DocRetriever = default_context['DocRetriever']
        res = doc_retriever.invoke('湖南大众传媒职业技术学院2023届毕业生就业质量年度报告')
        print(res)
        self.assertIsNotNone(res)

    def test_merge_with_common_prefix(self):
        merged = DocRetriever.merge_with_common_prefix("你好，我是Leo", "你好，我是Tony")
        self.assertEquals("你好，我是Leo\nTony", merged)
