# name: fay_agent.py
# description: Agentic tool 完善模型回答
# author: acxgdxy,xiongxiao31
# time: 2024/07/03
# 请不要用GPT生成代码中的注释，谢谢。
from langchain.tools import BaseTool
from typing import Any
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
