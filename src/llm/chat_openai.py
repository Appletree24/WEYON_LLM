from langchain_openai import ChatOpenAI

import llm


@llm.register
class ServeChatModel(ChatOpenAI):

    def __init__(self, logger, serve_chat_model_config):
        super().__init__(**serve_chat_model_config)

        logger.info(f"ChatModel initialized with {serve_chat_model_config['openai_api_base']}")
