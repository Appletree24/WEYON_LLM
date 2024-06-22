import llm
from langchain_openai import ChatOpenAI


@llm.register
class ServeChatModel(ChatOpenAI):

    def __init__(self):
        super().__init__(model="Qwen2-Local",
                         max_tokens=100000,
                         openai_api_base="http://192.168.100.111:9997/v1",
                         openai_api_key="dummy")
