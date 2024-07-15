#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Logical_Semantic_routing.py
# @Time      :2024/07/15 11:09:59
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 路由模块中的Logical Semantic Routing
# @Version   :1.0
# @Conda Env : rag_zzh
# 请不要用GPT生成代码中的注释，谢谢。

from typing import Literal

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain_openai import ChatOpenAI


class RouteQuery(BaseModel):
    datasource: Literal["python_docs", "js_docs", "golang_docs"] = Field(
        ...,
        description="Given a user question choose which datasource would be most relevant for answering their question",
    )


llm = ChatOpenAI(model='qwen2-pro', max_tokens=5000, max_retries=2, api_key="dummy",
                 base_url="http://192.168.100.111:8000/v1", streaming=True, verbose=True)

structured_llm = llm.with_structured_output(RouteQuery)
