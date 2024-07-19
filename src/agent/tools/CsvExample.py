from langchain.tools import BaseTool
from langchain_core.pydantic_v1 import BaseModel
from langchain_core.vectorstores import VectorStoreRetriever
from typing import Any


class BaseQdrantTool(BaseModel):
    """与Qdrant交互的基本工具"""
    qdrant_retriever: VectorStoreRetriever

    class Config(BaseTool.Config):
        pass


class CsvExample(BaseQdrantTool, BaseTool):
    name: str = "csv_example"
    description: str = "当确定进行sql查询时，一定一定一定调用此工具进行向量数据库检索，查询相关样例以辅助模型生成"

    def _run(self, para) -> str:
        try:
            import re
            RAG_ENHANCE_PROMPT = str(self.qdrant_retriever.invoke(para))
            text = RAG_ENHANCE_PROMPT
            print(text, type(text))
            # 使用正则表达式提取所有相关信息
            pattern = re.compile(r"咨询问题描述: (.*?)\\nMySQL文本: (.*?)\\n", re.DOTALL)
            matches = pattern.findall(text)

            # 构建格式化输出
            formatted_text = ""
            for match in matches:
                question = match[0]
                answer = match[1]
                formatted_text += f"Q:咨询问题描述: {question}\nA:MySQL文本: {answer}\n\n"

            # 移除最后一个多余的换行符
            formatted_text = formatted_text.strip()

            print("asdasd", formatted_text)
            return f"以下是查询出向量数据库中相似的辅助内容：\n {formatted_text}"
        except Exception as e:
            print("错误", e)
            return "获取就业数据失败"
