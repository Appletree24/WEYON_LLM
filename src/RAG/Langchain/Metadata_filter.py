#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Metadata_filter.py
# @Time      :2024/07/15 15:43:59
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 元数据过滤
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Literal, Optional, Tuple
import datetime
from langchain_community.document_loaders import YoutubeLoader

docs = YoutubeLoader.from_youtube_url(
    "https://www.youtube.com/watch?v=pbAd8O1Lvm4", add_video_info=True
).load()


class TutorialSearch(BaseModel):
    """Search over a database of tutorial videos about a software library."""

    content_search: str = Field(
        ...,
        description="Similarity search query applied to video transcripts.",
    )
    title_search: str = Field(
        ...,
        description=(
            "Alternate version of the content search query to apply to video titles. "
            "Should be succinct and only include key words that could be in a video "
            "title."
        ),
    )
    min_view_count: Optional[int] = Field(
        None,
        description="Minimum view count filter, inclusive. Only use if explicitly specified.",
    )
    max_view_count: Optional[int] = Field(
        None,
        description="Maximum view count filter, exclusive. Only use if explicitly specified.",
    )
    earliest_publish_date: Optional[datetime.date] = Field(
        None,
        description="Earliest publish date filter, inclusive. Only use if explicitly specified.",
    )
    latest_publish_date: Optional[datetime.date] = Field(
        None,
        description="Latest publish date filter, exclusive. Only use if explicitly specified.",
    )
    min_length_sec: Optional[int] = Field(
        None,
        description="Minimum video length in seconds, inclusive. Only use if explicitly specified.",
    )
    max_length_sec: Optional[int] = Field(
        None,
        description="Maximum video length in seconds, exclusive. Only use if explicitly specified.",
    )

    def pretty_print(self) -> None:
        for field in self.__fields__:
            if getattr(self, field) is not None and getattr(self, field) != getattr(
                self.__fields__[field], "default", None
            ):
                print(f"{field}: {getattr(self, field)}")


system = """You are an expert at converting user questions into database queries. \
You have access to a database of tutorial videos about a software library for building LLM-powered applications. \
Given a question, return a database query optimized to retrieve the most relevant results.

If there are acronyms or words you are not familiar with, do not try to rephrase them."""
prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system),
        ("human", "{question}"),
    ]
)
llm = ChatOpenAI(model='qwen2-pro', max_tokens=5000, max_retries=2, api_key="dummy",
                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True)
structured_llm = llm.with_structured_output(TutorialSearch)
query_analyzer = prompt | structured_llm
query_analyzer.invoke({"question": "rag from scratch"}).pretty_print()


# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain_openai import ChatOpenAI
# from langchain_community.document_loaders import Docx2txtLoader
# from langchain_core.prompts import ChatPromptTemplate
# from langchain_openai import ChatOpenAI
# from langchain_core.pydantic_v1 import BaseModel, Field
#
#
# class UniversitySearch(BaseModel):
#    source: str = Field(
#        ...,
#        description="The source of the document"
#    )
#
#    def pretty_print(self) -> None:
#        for field in self.__fields__:
#            if getattr(self, field) is not None and getattr(self, field) != getattr(
#                self.__fields__[field], "default", None
#            ):
#                print(f"{field}: {getattr(self, field)}")
#
#
# system_prompt = """
# 您是将用户问题转化为数据库查询的专家.
# 你可以访问一个数据库，其中有关于构建 LLM 驱动的应用程序的软件库的教程视频。
# 给定一个问题，返回一个经过优化的数据库查询，以检索最相关的结果.
#
# 如果有您不熟悉的缩略词或单词，请不要尝试重新表述。
# """
#
# prompt = ChatPromptTemplate.from_messages(
#    [
#        ("system", system_prompt),
#        ("human", "{question}"),
#    ]
# )
#
# llm = ChatOpenAI(model='qwen2-pro', max_tokens=5000, max_retries=2, api_key="dummy",
#                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True)
#
# structured_llm = llm.with_structured_output(UniversitySearch)
#
# loader = Docx2txtLoader(file_path='WEYON_LLM/resources/doc/Chuanmei.docx')
#
# docs = loader.load()
#
# query_analyzer = prompt | structured_llm
#
# response = query_analyzer.invoke({"question": "rag from scratch"})
# print(response)
#
