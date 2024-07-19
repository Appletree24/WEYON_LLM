# name: Analysis.py
# description: Agentic tool 完善模型回答
# author: acxgdxy,woshixiong
# time: 2024/07/03
# 请不要用GPT生成代码中的注释，谢谢。
from typing import Any, Dict, Optional, Sequence, Type, Union
from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel, Field
from typing import Any


class _QueryAnalysisInput(BaseModel):
    query: str = Field(..., description="A detailed and correct SQL query.")


class Analysis(BaseTool):
    name: str = "Analysis"
    description: str = "确保在输出最终结果之前调用该工具，记住无论如何都要实现此工具"
    args_schema: Type[BaseModel] = _QueryAnalysisInput

    def _run(self, para) -> str:
        try:
            # print("para", para, type(para))
            data = para
            return f"{data}，这是查询出来的数据信息，请你根据这个数据查询结果分析数据得出一定结论并延长文本回答."
        except Exception as e:
            print("错误", e)
            return "获取就业数据失败"
