# name: ListSql.py
# description: agent中与业务相关的sql toll
# author: acxgdxy
# time: 2024/07/02
import pymysql
from pymysql.constants import CLIENT
from langchain.tools import BaseTool

from agent.data.province1 import Province1
from typing import Any
import json


class ListSql(BaseTool):
    name = "ListSql"
    description = "用于查询公司业务中的就业数据"

    def __init__(self):
        super().__init__()

    async def _arun(
            self,
            *args: Any,
            **kwargs: Any,
    ) -> Any:
        pass

    def _run(self, para):
        try:
            # 连接数据库
            # print("para", para, type(para))
            json_object = json.loads(para)
            if json_object.get('sql'):
                sql = json_object['sql']
            else:
                sql = json_object['query']
            province1 = Province1()
            sql = province1.replace_quoted_values(sql)
            conn = pymysql.connect(host='am-wz9el267w54i2r7ip131930o.ads.aliyuncs.com', user='ai_user',
                                   password='Ai@use_15379',
                                   database='ai_use',
                                   port=3306,
                                   charset='utf8',
                                   client_flag=CLIENT.MULTI_STATEMENTS,)
            # print('连接数据库成功！')
            cursor = conn.cursor()
            cursor.execute(sql)
            data = cursor.fetchall()
            conn.commit()
            conn.close()
            # print(data)
            return f"查询已经成功，数据如下{data}"
        except Exception as e:
            print("错误", e)
            return "获取就业数据失败"


if __name__ == '__main__':
    tool = ListSql()
    result = tool.run({"sql": "asdasd"})
    print(result)
