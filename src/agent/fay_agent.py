# name: fay_agent.py
# description: agent主体代码
# author: acxgdxy
# time: 2024/07/03
import os
import math

from agent.tools.MyTimer import MyTimer
from agent.tools.Weather import Weather
from agent.tools.QueryTime import QueryTime
from agent.tools.PythonExecutor import PythonExecutor
from agent.tools.WebPageRetriever import WebPageRetriever
from agent.tools.WebPageScraper import WebPageScraper
from agent.tools.ListSql import ListSql
from agent.data.province import ProvinceData
from agent.data.city import CityData

from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent, Tool
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain_openai import ChatOpenAI
from langchain import PromptTemplate
from langchain_community.utilities import SQLDatabase
from langchain_community.callbacks import get_openai_callback
from langchain_community.tools.sql_database.tool import (
    InfoSQLDatabaseTool,
    ListSQLDatabaseTool,
    QuerySQLCheckerTool,
    QuerySQLDataBaseTool,
)

import utils.config_util as utils
from agent.toolkit.toolkit import MySQLDatabaseToolkit

BASE_DIR = os.path.dirname(os.path.abspath(__file__))



class FayAgentCore():
    def __init__(self):
        utils.load_config()
        if str(utils.tavily_api_key) != '':
            os.environ["TAVILY_API_KEY"] = utils.tavily_api_key
        os.environ["OPENAI_API_KEY"] = utils.key_gpt_api_key
        os.environ["OPENAI_API_BASE"] = utils.gpt_base_url
        # 创建llm
        self.llm = ChatOpenAI(model=utils.gpt_model_engine)
        # 保存基本信息到记忆
        utils.load_config()
        # 内存保存聊天历史
        self.chat_history = []

        db_user = "root"
        db_password = "AI20240520"
        db_host = "192.168.100.111"
        db_name = "ai_use"
        db_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"
        db = SQLDatabase.from_uri(db_uri)
        self.db = db

        # 创建agent chain
        my_timer = MyTimer()
        weather_tool = Weather()
        query_time = QueryTime()
        # query_timer_db_tool = QueryTimerDB()
        # delete_timer_tool = DeleteTimer()
        python_executor = PythonExecutor()
        web_page_retriever = WebPageRetriever()
        web_page_scraper = WebPageScraper()
        # list_sql = ListSql()
        # toolkit = MySQLDatabaseToolkit(db=db, llm=self.llm)
        # tools = toolkit.get_tools()
        """Get the tools in the toolkit."""
        list_sql_database_tool = ListSQLDatabaseTool(db=self.db)
        # info_sql_database_tool_description = (
        #     "Input to this tool is a comma-separated list of tables, output is the "
        #     "schema and sample rows for those tables. "
        #     "Be sure that the tables actually exist by calling "
        #     f"{list_sql_database_tool.name} first! "
        #     "Example Input: table1, table2, table3"
        # )
        info_sql_database_tool = InfoSQLDatabaseTool(
            db=self.db,
            # description=info_sql_database_tool_description
        )
        # query_sql_database_tool_description = (
        #     "Input to this tool is a detailed and correct SQL query, output is a "
        #     "result from the database. If the query is not correct, an error message "
        #     "will be returned. If an error is returned, rewrite the query, check the "
        #     "query, and try again. If you encounter an issue with Unknown column "
        #     f"'xxxx' in 'field list', use {info_sql_database_tool.name} "
        #     "to query the correct table fields."
        # )
        query_sql_database_tool = QuerySQLDataBaseTool(
            db=self.db,
            # description=query_sql_database_tool_description
        )
        # query_sql_checker_tool_description = (
        #     "Use this tool to double check if your query is correct before executing "
        #     "it. Always use this tool before executing a query with "
        #     f"{query_sql_database_tool.name}!"
        # )
        query_sql_checker_tool = QuerySQLCheckerTool(
            db=self.db, llm=self.llm,
            # description=query_sql_checker_tool_description
        )

        # 输入数据处理
        self.province_data = ProvinceData()
        self.city_data = CityData()

        self.tools = [
            # Tool(
            #     name=python_executor.name,
            #     func=python_executor.run,
            #     description=python_executor.description
            # ),
            # Tool(
            #     name=list_sql.name,
            #     func=list_sql.run,
            #     description=list_sql.description
            # ),
            Tool(
                name=list_sql_database_tool.name,
                func=list_sql_database_tool.run,
                description=list_sql_database_tool.description,
            ),
            Tool(
                name=info_sql_database_tool.name,
                func=info_sql_database_tool.run,
                description=info_sql_database_tool.description
            ),
            Tool(
                name=query_sql_checker_tool.name,
                func=query_sql_checker_tool.run,
                description=query_sql_checker_tool.description
            ),
            Tool(
                name=query_sql_database_tool.name,
                func=query_sql_database_tool.run,
                description=query_sql_database_tool.description
            ),


            Tool(
                name=my_timer.name,
                func=my_timer.run,
                description=my_timer.description
            ),
            Tool(
                name=weather_tool.name,
                func=weather_tool.run,
                description=weather_tool.description
            ),
            Tool(
                name=web_page_retriever.name,
                func=web_page_retriever.run,
                description=web_page_retriever.description
            ),
            Tool(
                name=web_page_scraper.name,
                func=web_page_scraper.run,
                description=web_page_scraper.description
            ),
            Tool(
                name=query_time.name,
                func=query_time.run,
                description=query_time.description
            )
        ]
        # self.tools = self.tools.append(tools)
        # print(type(self.tools))
        # print(type(tools))
        if str(utils.tavily_api_key) != '':
            self.tools.append(TavilySearchResults(max_results=1))
        # https://python.langchain.com/v0.1/docs/modules/agents/agent_types/react/   用于记忆上下文
        # prompt = hub.pull("hwchase17/react-chat")
        # print(prompt)
        # agent用于执行任务
        with open(os.path.join(BASE_DIR, 'template.txt'), "r", encoding='utf-8') as f:
            template = f.read()
            # 我想要知道2021届的就业数据
            # 查询长沙的就业数据
            # 查询湖南的就业数据
            prompt = PromptTemplate(
                input_variables=[
                    'agent_scratchpad',
                    'chat_history',
                    'input',
                    'tool_names',
                    'tools'
                ],
                metadata={
                    'lc_hub_owner': 'hwchase17',
                    'lc_hub_repo': 'react-chat',
                    'lc_hub_commit_hash': '3ecd5f710db438a9cf3773c57d6ac8951eefd2cd9a9b2a0026a65a0893b86a6e'
                },
                template=template,
            )
            agent = create_react_agent(self.llm, self.tools, prompt)

            # 通过传入agent和tools来创建一个agent executor
            self.agent = AgentExecutor(agent=agent, tools=self.tools, verbose=True, handle_parsing_errors=True)
            self.total_tokens = 0
            self.total_cost = 0

    # 记忆prompt
    def format_history_str(self, history_list):
        result = ''
        for history in history_list:
            result = "Human: {input}\nAI: {output}\n".format(input=history['input'], output=history['output'])
        return result

    def run(self, input_text):
        result = ""
        history = ""
        history = self.format_history_str(self.chat_history)
        try:
            input_text = input_text.replace('主人语音说了：', '').replace('主人文字说了：', '')
            # input_text = self.province_data.replace_region(input_text)
            input_text = self.city_data.replace_city(input_text)
            with get_openai_callback() as cb:
                result = self.agent.invoke({"input": input_text, "chat_history": history})
                re = result['output']
                self.total_tokens = self.total_tokens + cb.total_tokens
                self.total_cost = self.total_cost + cb.total_cost

        except Exception as e:
            print(e)

        re = "执行完毕" if re is None or re == "N/A" else re
        chat_text = re

        # 保存到记忆流和聊天对话且控制记忆的条数
        self.chat_history.append(result)
        if len(self.chat_history) > 5:
            self.chat_history.pop(0)

        return False, chat_text


if __name__ == "__main__":
    agent = FayAgentCore()
    while True:
        user_input = input("User: ")
        if user_input.lower() in ["quit", "exit", "q"]:
            print("Goodbye!")
            break
        agent.run(user_input)
