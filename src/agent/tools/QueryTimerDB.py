import abc, os
import sqlite3
from typing import Any
import ast

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
from langchain.tools import BaseTool


class QueryTimerDB(BaseTool, abc.ABC):
    name = "QueryTimerDB"
    description = "用于查询所有日程，返回的数据里包含3个参数:时间、循环规则（如:'1000100'代表星期一和星期五循环，'0000000'代表不循环）、执行的事项"

    def __init__(self):
        super().__init__()

    async def _arun(self, *args: Any, **kwargs: Any) -> Any:
        # 用例中没有用到 arun 不予具体实现
        pass


    def _run(self, para) -> str:
        conn = sqlite3.connect(os.path.join(BASE_DIR, 'timer.db'))
        cursor = conn.cursor()

        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        # 如果表不存在则创建表
        if ('timer',) not in tables:
            cursor.execute('''
            CREATE TABLE timer (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                time TEXT NOT NULL,
                repeat_rule TEXT NOT NULL,
                task TEXT NOT NULL
            )
            ''')
            print("Created table 'timer'")

        # 执行查询
        cursor.execute("SELECT * FROM timer")
        # 获取所有记录
        rows = cursor.fetchall()
        # 拼接结果
        result = ""
        for row in rows:
            result = result +  str(row) + "\n"
        conn.commit()
        conn.close()
        return result


if __name__ == "__main__":
    tool = QueryTimerDB()
    result = tool.run("")
    print(result)
