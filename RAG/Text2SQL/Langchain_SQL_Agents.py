#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :Langchain_SQL_Agents.py
# @Time      :2024/07/05 14:30:15
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: 利用Langchain框架编写的Agentic RAG For nl2SQL
# @Version   :2.0
# 请不要用GPT生成代码中的注释，谢谢。

# 飞书内部文档链接，有对此文件代码的解释：https://cqqsgt4nbl1.feishu.cn/wiki/Hr3ewZlTOikzqxkFZWHcPflEnxb?from=from_copylink

from urllib.parse import quote_plus
import os
import re
import ast
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain.agents.agent_toolkits import create_retriever_tool
from langgraph.prebuilt import create_react_agent
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import ChatOpenAI
from langchain_community.utilities import SQLDatabase
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.prompts import PromptTemplate
from langchain.callbacks.base import BaseCallbackHandler
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain.memory.buffer import ConversationBufferMemory
from langchain_community.document_loaders.csv_loader import CSVLoader
import logging

# 设置日志记录格式和级别
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 设置环境变量，用于配置OpenAI API和CUDA设备
os.environ["OPENAI_API_BASE"] = "http://192.168.100.111:8000/v1"
os.environ["OPENAI_API_KEY"] = "dummy"
# 这是之前0卡在跑模型，所以改成1卡了，可以按照需要自行注释与否
os.environ["CUDA_VISIBLE_DEVICES"] = "1"


# 初始化嵌入模型
embeeding_name = "thenlper/gte-large"
embeedings = HuggingFaceEmbeddings(model_name=embeeding_name)

# 加载CSV文件
loader = CSVLoader(file_path='WEYON_LLM/RAG/Text2SQL/Example_SQL.csv')
sample_sql = loader.load()

# 定义符合中文语系的文本分割器
chinese_text_splitter = RecursiveCharacterTextSplitter(chunk_size=1024, chunk_overlap=64, separators=[
    "\n\n",
    "\n",
    " ",
    ".",
    ",",
    "\u200B",  # 零宽度空格
    "\uff0c",  # 全角逗号
    "\u3001",  # 顿号
    "\uff0e",  # 全角句号
    "\u3002",  # 句号
    "",
])

# 分割样本SQL文档
sql_example_chunks = chinese_text_splitter.split_documents(sample_sql)


# 配置数据库连接
db_user = "xxxx"
db_password = "xxxx"
db_host = "xxxxx"
db_name = "xxxx"
db_uri = f"mysql+pymysql://{db_user}:{db_password}@{db_host}/{db_name}"

db = SQLDatabase.from_uri(db_uri)

# 定义中文系统消息模板
# ATTENTION LIMIT 5 定义在System prompt中，可以修改为自己要的参数
chinese_system_ = """
你是一个与 SQL 数据库交互的代理。
给定一个输入问题，创建一个语法正确的 MySQL 查询来运行，然后查看查询结果并返回答案。
除非用户指定了希望获得的示例的具体数量，否则始终将查询结果限制为最多 5 个。
您可以根据相关列对结果进行排序，以返回数据库中最相关、最准确的示例。
切勿查询特定表中的所有列，只查询问题中的相关列。
您可以使用与数据库交互的工具。
注意：如果用户使用了专有名词的缩写，你可以按照自己的理解将缩写补全为全称，并应用在生成的SQL语句以及后续的查询中！
例如长理是长沙理工大学，湘大是湘潭大学，西农是西北农林科技大学,南林是南京林业大学,等等,按照你的预训练数据以及我给出的规则，之后可以自行补全。
只能使用指定的工具。只能使用工具返回的信息来构建您的最终答案。
执行查询前必须仔细检查。如果在执行查询时出现错误，请重写查询并再试一次。

切勿对数据库执行任何 DML 语句（INSERT、UPDATE、DELETE、DROP 等）。

您可以访问以下表：{table_names}
此表的DDL语句为:
        ```sql
            create table dw_s_employment_company
(
    xxdm       varchar charset utf8 null comment '学校代码',
    xxid       varchar charset utf8 null comment '学校ID',
    xxmc       varchar charset utf8 null comment '学校名称',
    xxsf       varchar charset utf8 null comment '学校省份',
    xxcs       varchar charset utf8 null comment '学校城市',
    bxcc       varchar charset utf8 null comment '办学层次',
    xxcc       varchar charset utf8 null comment '学校层次',
    xxlx       varchar charset utf8 null comment '学校类型',
    jb         varchar charset utf8 null comment '届别',
    yx         varchar charset utf8 null comment '院系',
    zydm       varchar charset utf8 null comment '专业代码',
    zy         varchar charset utf8 null comment '专业',
    xkml       varchar charset utf8 null comment '学科门类',
    zydl       varchar charset utf8 null comment '专业大类',
    zyfx       varchar charset utf8 null comment '专业方向',
    bj         varchar charset utf8 null comment '班级',
    xm         varchar charset utf8 null comment '姓名',
    xh         varchar charset utf8 null comment '学号',
    sfzhm      varchar charset utf8 null comment '身份证号码',
    xl         varchar charset utf8 null comment '学历',
    xb         varchar charset utf8 null comment '性别',
    sfslb      varchar charset utf8 null comment '师范生类别',
    jyknlb     varchar charset utf8 null comment '困难生类别',
    mz         varchar charset utf8 null comment '民族',
    kslb       varchar charset utf8 null comment '城乡生源',
    syszddm    varchar charset utf8 null comment '生源所在地代码',
    xl_c       varchar charset utf8 null comment '学历_合并',
    sfslb_c    varchar charset utf8 null comment '师范生类别_合并',
    jyknlb_c   varchar charset utf8 null comment '困难生类别_合并',
    ssmz       varchar charset utf8 null comment '是否少数民族',
    ssmz_01    int                  null comment '少数民族人数',
    syjjq      varchar charset utf8 null comment '生源经济区',
    sysf       varchar charset utf8 null comment '生源省份',
    sycs       varchar charset utf8 null comment '生源城市',
    bzr        varchar charset utf8 null comment '班主任/辅导员',
    lsbyqx     varchar charset utf8 null comment '是否落实毕业去向',
    lsbyqx_01  int                  null comment '落实毕业去向人数',
    byqx1      varchar charset utf8 null comment '毕业去向一级分类',
    byqx2      varchar charset utf8 null comment '毕业去向二级分类',
    byqx3      varchar charset utf8 null comment '毕业去向三级分类',
    byqxdm     varchar charset utf8 null comment '毕业去向代码',
    byqx       varchar charset utf8 null comment '毕业去向',
    dwjy       varchar charset utf8 null comment '是否单位就业',
    dwjy_01    int                  null comment '单位就业人数',
    zzcy       varchar charset utf8 null comment '是否自主创业',
    zzcy_01    int                  null comment '自主创业人数',
    zyzy       varchar charset utf8 null comment '是否自由职业',
    zyzy_01    int                  null comment '自由职业人数',
    jnsx       varchar charset utf8 null comment '是否境内升学',
    jnsx_01    int                  null comment '境内升学人数',
    jwlx       varchar charset utf8 null comment '是否境外留学',
    jwlx_01    int                  null comment '境外留学人数',
    sx_01      int                  null comment '升学人数',
    djy        varchar charset utf8 null comment '是否待就业',
    djy_01     int                  null comment '待就业人数',
    zbjy       varchar charset utf8 null comment '是否暂不就业',
    zbjy_01    int                  null comment '暂不就业人数',
    lhjy       varchar charset utf8 null comment '是否灵活就业',
    lhjy_01    int                  null comment '灵活就业人数',
    lhjylb     varchar charset utf8 null comment '灵活就业类别',
    dwmc       varchar charset utf8 null comment '单位名称',
    dwszddm    varchar charset utf8 null comment '单位所在地代码',
    dwzzjg     varchar charset utf8 null comment '统一社会信用代码/组织机构代码',
    dwhy       varchar charset utf8 null comment '单位行业',
    dwxz       varchar charset utf8 null comment '单位性质',
    gzzwlb     varchar charset utf8 null comment '工作职位类别',
    sfmc       varchar charset utf8 null comment '就业省份',
    sqmc       varchar charset utf8 null comment '就业城市',
    qxmc       varchar charset utf8 null comment '就业区县',
    gxsjy      varchar charset utf8 null comment '是否高校所在省就业',
    gxsjy_01   int                  null comment '高校所在省就业人数',
    bshjy      varchar charset utf8 null comment '是否高校所在省会就业',
    bshjy_01   int                  null comment '高校所在省会就业人数',
    bcsjy      varchar charset utf8 null comment '是否高校所在城市就业',
    bcsjy_01   int                  null comment '高校所在城市就业人数',
    sysjy      varchar charset utf8 null comment '是否生源省就业',
    sysjy_01   int                  null comment '生源省就业人数',
    jcjy       varchar charset utf8 null comment '是否基层就业',
    jcjy_01    int                  null comment '基层就业人数',
    yxid       varchar charset utf8 null comment '院系ID',
    id         varchar charset utf8 null comment '主键ID',
    xysh       varchar charset utf8 null comment '学院审核_生源',
    xxsh       varchar charset utf8 null comment '学校审核_生源',
    xysh_jy    varchar charset utf8 null comment '学院审核_就业',
    xxsh_jy    varchar charset utf8 null comment '学校审核+_就业',
    qypf       varchar charset utf8 null comment '企业评分',
    qybq       varchar charset utf8 null comment '企业标签',
    qygm       varchar charset utf8 null comment '企业规模',
    jjq        varchar charset utf8 null comment '就业经济区',
    jjj        varchar charset utf8 null comment '是否京津冀经济圈就业',
    cjjjd      varchar charset utf8 null comment '是否长江经济带就业',
    csj        varchar charset utf8 null comment '是否长江三角洲就业',
    yga        varchar charset utf8 null comment '是否粤港澳大湾区就业',
    hhly       varchar charset utf8 null comment '是否黄河流域就业',
    ydyl       varchar charset utf8 null comment '是否一带一路经济带就业',
    zjsjz      varchar charset utf8 null comment '是否珠江三角洲就业',
    csfj       varchar charset utf8 null comment '城市分级',
    jkbydq     varchar charset utf8 null comment '是否艰苦边远地区就业',
    sdbk       varchar charset utf8 null comment '四大板块',
    xblhxtd    varchar charset utf8 null comment '是否西部陆海新通道就业',
    jtmc       varchar charset utf8 null comment '集团名称',
    hysl       varchar charset utf8 null comment '行业大类',
    yq         varchar charset utf8 null comment '是否央企',
    sj500q     varchar charset utf8 null comment '是否世界500强',
    zg500q_nd  varchar charset utf8 null comment '是否中国500强',
    zg500q     varchar charset utf8 null comment '是否中国500强（内地）',
    my500q     varchar charset utf8 null comment '是否民营500强',
    hy500q_s   varchar charset utf8 null comment '是否行业500强_总',
    jx500q     varchar charset utf8 null comment '是否机械工业500强',
    ny500q     varchar charset utf8 null comment '是否能源企业500强',
    qqny500q   varchar charset utf8 null comment '是否全球新能源企业500强',
    jt500q     varchar charset utf8 null comment '是否交通500强',
    ssgs       varchar charset utf8 null comment '是否上市公司',
    hy100q_s   varchar charset utf8 null comment '是否行业100强_总',
    spzz100q   varchar charset utf8 null comment '是否食品制造100强',
    zbzz100q   varchar charset utf8 null comment '是否装备制造100强',
    zlxxcy100q varchar charset utf8 null comment '是否战略新兴产业100强',
    ypls100q   varchar charset utf8 null comment '是否药品零售企业100强',
    yppf100q   varchar charset utf8 null comment '是否药品批发企业100强',
    wlqy100q   varchar charset utf8 null comment '是否物流企业50强',
    mywl100q   varchar charset utf8 null comment '是否民营物流企业50强',
    kjsws100q  varchar charset utf8 null comment '是否会计事务所100强',
    ylsfqy     varchar charset utf8 null comment '是否一流示范企业',
    ylzjtxsf   varchar charset utf8 null comment '是否一流专精特新示范企业',
    yxlssws    varchar charset utf8 null comment '是否优秀律师事务所',
    yhjr       varchar charset utf8 null comment '是否银行业金融机构',
    yljgdj     varchar charset utf8 null comment '是否医疗机构等级',
    xjr        varchar charset utf8 null comment '是否小巨人企业',
    kyys       varchar charset utf8 null comment '是否科研院所',
    sydw       varchar charset utf8 null comment '是否事业单位',
    zfjg       varchar charset utf8 null comment '是否政府机关',
    tbbq       varchar charset utf8 null comment '是否头部标签',
    tbbqjh     varchar charset utf8 null comment '头部标签聚合',
    zrs        int                  null comment '总人数',
    primary key (__adb_auto_id__)

""".format(table_names=db.get_usable_table_names())

# 增加上下文对话历史
chinese_system = chinese_system_ + "上下文对话历史为{chat_history}"

# 定义SQL问题提示模板
CUSTOM_SQL_QUESTION_PROMPT = PromptTemplate.from_template(chinese_system)

# 初始化对话历史缓冲区
chat_memory = ConversationBufferMemory(
    memory_key="chat_history", return_messages=True)

# 初始化LLM模型, qwen2-pro目前在服务器上的max_model_len是1w tokens
llm = ChatOpenAI(model="qwen2-pro",
                 max_tokens=5000, max_retries=2)

# 创建SQL数据库工具包
toolkit = SQLDatabaseToolkit(db=db, llm=llm)

# 获取工具
tools = toolkit.get_tools()


# 初始化Chroma数据库
db_chroma = Chroma.from_documents(
    sql_example_chunks, embeedings, persist_directory="example_sql")

# 初始化数据库检索器，返回值数据类型是List，大小为search_kwargs中的k值
db_retriever = db_chroma.as_retriever(search_kwargs={"k": 3})

# 生成增强RAG提示
RAG_ENHANCE_PROMPT = db_retriever.invoke(
    "我想查询来自国科大的学生就业数据,请编写SQL语句,使用模糊查询限定条件,不要使用LIMIT限制")

# 定义系统消息
system_message = SystemMessage(content=chinese_system+str(RAG_ENHANCE_PROMPT))

# 创建React代理
agent = create_react_agent(
    llm, tools, messages_modifier=system_message)

# 执行代理查询
for s in agent.stream(
    {"messages": [HumanMessage(
        content="我想查询来自国科大的学生就业数据,请编写SQL语句,使用模糊查询限定条件,不要使用LIMIT限制")]}
):
    print(s)
    print("------------------------------------------------------------------------------------")

# 定义SQL前缀模板,待测试是否会比中文prompt效果更好
# SQL_PREFIX = """You are an agent designed to interact with a SQL database.
# Given an input question, create a syntactically correct SQLite query to run, then look at the results of the query and return the answer.
# Unless the user specifies a specific number of examples they wish to obtain, always limit your query to at most 5 results.
# You can order the results by a relevant column to return the most interesting examples in the database.
# Never query for all the columns from a specific table, only ask for the relevant columns given the question.
# You have access to tools for interacting with the database.
# Only use the below tools. Only use the information returned by the below tools to construct your final answer.
# You MUST double check your query before executing it. If you get an error while executing a query, rewrite the query and try again.
#
# DO NOT make any DML statements (INSERT, UPDATE, DELETE, DROP etc.) to the database.
#
# To start you should ALWAYS look at the tables in the database to see what you can query.
# Do NOT skip this step.
# Then you should query the schema of the most relevant tables."""


# 定义PromptPrinter类，用于打印输入给LLM的Prompt
# class PromptPrinter(BaseCallbackHandler):
#    def on_llm_start(self, serialized, prompts, **kwargs):
#        print(f"输入给LLM的Prompt为:{prompts[0]}")

# 定义PromptCapturingHandler类，用于捕获LLM的Prompt
# class PromptCapturingHandler(BaseCallbackHandler):
#    def __init__(self):
#        self.llm_prompts = []
#
#    def on_llm_end(self, serialized, prompts, **kwargs):
#        self.llm_prompts.append(prompts)

# 定义查询结果格式化函数
#
#
# def query_as_list(db, query):
#    res = db.run(query)
#    res = [el for sub in ast.literal_eval(res) for el in sub if el]
#    res = [re.sub(r"\b\d+\b", "", string).strip() for string in res]
#    return list(set(res))
