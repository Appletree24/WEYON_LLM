from unittest import TestCase
from llm import default_register


class TestServeChatModel(TestCase):

    def test_serve_chat_model(self):
        """
        测试ServeChatModel类
        """
        # 测试ServeChatModel是否成功注册到default_register中
        from llm import chat_openai
        model = default_register.get_bean("ServeChatModel")
        self.assertIsNotNone(model)

    def test_serve_chat_model_invoke(self):
        """
        测试ServeChatModel类的invoke方法
        """
        from llm import chat_openai
        model = default_register.get_bean("ServeChatModel")
        res = model.invoke("Hello, how are you?")
        self.assertIsNotNone(res)
        self.assertTrue(res.content)
