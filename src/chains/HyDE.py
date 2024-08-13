from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from pydantic import BaseModel, Field

import chains
from llm import chat_openai
from logs import get_logger
from retriever import doc_retriever

logger = get_logger(__name__)


class HypotheticalDocument(BaseModel):
    title: str = Field(description="文章标题")
    document: str = Field(description="文章内容")


template = """
## 指令：写一篇报告来回答用户的问题
## 用户问题：{question}

{output_format}
"""


@chains.register
def hy_de(ServeChatModel):
    chat_model: chat_openai.ChatOpenAI = ServeChatModel
    hyde_parser = PydanticOutputParser(pydantic_object=HypotheticalDocument)
    prompt_template = PromptTemplate(template=template,
                                     input_variables=["question"],
                                     partial_variables={
                                         'output_format': hyde_parser.get_format_instructions()})
    return prompt_template | ServeChatModel | hyde_parser


def log(p: HypotheticalDocument):
    logger.debug(p)
    return p.document


@chains.register
def hyde_rag(hy_de, DocRetriever):
    retriever: doc_retriever.BaseRetriever = DocRetriever
    return hy_de | RunnableLambda(lambda x: log(x)) | retriever
