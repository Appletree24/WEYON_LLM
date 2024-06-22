from unittest import TestCase

import llm
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
        self.assertIsNotNone(res.content)

    def test_llm_register(self):
        """
        测试llm.register函数
        """
        from langchain_openai import ChatOpenAI
        @llm.register
        def chat():
            return ChatOpenAI(model="Qwen2-Local",
                              max_tokens=100000,
                              openai_api_base="http://192.168.100.111:9997/v1",
                              openai_api_key="dummy")

        model = default_register.get_bean("chat")
        self.assertIsNotNone(model)
        res = model.invoke("Hello, how are you?")
        self.assertIsNotNone(res.content)
