from unittest import TestCase

import llm
from llm import chat_openai
from llm import default_register


class TestServeChatModel(TestCase):
    _ = chat_openai

    def test_serve_chat_model(self):
        """
        测试ServeChatModel类
        """
        # 测试ServeChatModel是否成功注册到default_register中
        model = default_register.get_bean("ServeChatModel")
        self.assertIsNotNone(model)

    def test_serve_chat_model_invoke(self):
        """
        测试ServeChatModel类的invoke方法
        """
        model = default_register.get_bean("ServeChatModel")
        res = model.invoke("Hello, how are you?")
        self.assertIsNotNone(res.content)

    def test_llm_register(self):
        """
        测试llm.register函数
        """
        from langchain_openai import ChatOpenAI
        @llm.register
        def chat(logger):
            logger.info("Chat model loaded")
            config = default_register.get('serve_chat_model_config')
            return ChatOpenAI(model=config['model'],
                              max_tokens=config['max_tokens'],
                              openai_api_base=config['openai_api_base'],
                              openai_api_key=config['openai_api_key'])

        model = default_register.get_bean("chat")
        self.assertIsNotNone(model)
        res = model.invoke("Hello, how are you?")
        self.assertIsNotNone(res.content)
