from unittest import TestCase
from chains.profile_query import profile_query
from basic import default_context
from logs import get_logger


class Test(TestCase):
    def test_profile_query(self):
        _ = profile_query
        profile_chain = default_context.get_bean("profile_query")
        res = profile_chain.invoke({"question": '我是谁', "chat_history": '我是Leo'})
        get_logger('test_profile_query').info(res.content)
        self.assertIsNotNone(res)

    def test_profile_query_chain(self):
        profile_chain = default_context.get_bean("profile_query_chain")
        res = profile_chain.invoke(
            {"question": '全国各地的高效录取分数线', "chat_history": '我是一名计算机专业的大学生'})
        get_logger('test_profile_query_chain').info(res.content)
        self.assertIsNotNone(res)
