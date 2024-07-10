import pymysql
from pymysql.constants import CLIENT
from langchain.tools import BaseTool

from agent.data.province1 import Province1
from typing import Any
import json


class Analysis(BaseTool):
    name = "Analysis"
    description = "用于分析数据库中查询出来的数据"

    async def _arun(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> Any:
        pass

    def _run(self, para):
        try:
            print("para", para, type(para))
            data = para
            return f"{data}，这是查询出来的数据信息，请你根据这个数据查询结果分析数据并延长文本回答"
        except Exception as e:
            print("错误", e)
            return "获取就业数据失败"
