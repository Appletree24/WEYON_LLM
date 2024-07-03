#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Langchain_version.py
# @Time      :2024/07/03 15:42:44
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: Langchain版本的Text2SQL,没有Agent形式，效果好于llamaindex
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from langchain_community.utilities import SQLDatabase
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
import os
os.environ["OPENAI_API_BASE"] = "http://192.168.100.111:9997/v1"
os.environ["OPENAI_API_KEY"] = "dummy"

db_user = "root"
db_password = "AI20240520"
db_host = "192.168.100.111"
db_name = "ai_use"

# 研究院给的MySQL密码比较抽象，不符合MySQL规范，以后也避免使用特殊字符
# 如果要用阿里云，注释掉下述代码即可
# from urllib.parse import quote_plus
# db_user = "ai_user"
# db_password = quote_plus("Ai@use_15379")
# db_host = "am-wz9el267w54i2r7ip131930o.ads.aliyuncs.com"
# db_name = "ai_use"

db_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
db = SQLDatabase.from_uri(db_uri)

llm = ChatOpenAI(model="qwen2", max_tokens=100, max_retries=2)

chain = create_sql_query_chain()
execute_query = QuerySQLDataBaseTool(db=db)
write_query = create_sql_query_chain(llm, db)
chain = write_query | execute_query
chain.invoke({"question": "请告诉我表中sfslb字段的数据类型"})
