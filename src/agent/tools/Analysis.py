# name: Analysis.py
# description: Agentic tool 完善模型回答
# author: acxgdxy,woshixiong
# time: 2024/07/03
# 请不要用GPT生成代码中的注释，谢谢。
from langchain.tools import BaseTool
from typing import Any


class Analysis(BaseTool):
    name = "Analysis"
    # description = "在将最终查询结果输出给模型之前，一定要调用一次此工具，目的是为了增强模型回答的效果"
    description = "确保在输出最终结果之前调用该工具，记住无论如何都要实现此工具"

    async def _arun(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> Any:
        pass

    def _run(self, para):
        try:
            # print("para", para, type(para))
            data = para
            return f"{data}，这是查询出来的数据信息，请你根据这个数据查询结果分析数据得出一定结论并延长文本回答."
        except Exception as e:
            print("错误", e)
            return "获取就业数据失败"
