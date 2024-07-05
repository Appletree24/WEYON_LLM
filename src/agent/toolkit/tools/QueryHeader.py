from typing import Any, Dict, Optional, Sequence, Type, Union

from sqlalchemy.engine import Result

from langchain_core.pydantic_v1 import BaseModel, Field, root_validator

from langchain_core.language_models import BaseLanguageModel
from langchain_core.callbacks import (
    AsyncCallbackManagerForToolRun,
    CallbackManagerForToolRun,
)
from langchain_core.prompts import PromptTemplate
from langchain_community.utilities.sql_database import SQLDatabase
from langchain_core.tools import BaseTool
from langchain_community.tools.sql_database.prompt import QUERY_CHECKER


class BaseSQLDatabaseTool(BaseModel):
    """Base tool for interacting with a SQL database."""

    db: SQLDatabase = Field(exclude=True)

    class Config(BaseTool.Config):
        pass


class QueryHeader(BaseSQLDatabaseTool, BaseTool):
    # llm: BaseLanguageModel
    # llm_chain: Any = Field(init=False)
    name: str = "sql_query_header"
    description: str = """
        If you need to use sql for query, you MUST use this tool first. required to use this tool before all sql tools, this tool is used to query table structure information
    """

    async def _arun(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> Any:
        pass

    def _run(self, para):
        print("使用了没想到吧哈哈哈哈哈哈哈哈哈哈哈哈")
        data = self.db.get_table_info()
        return f"表格的结构信息： {data}"
