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

from operator import itemgetter
from langchain_community.utilities import SQLDatabase
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain.chains.sql_database.query import create_sql_query_chain
from langchain_openai import ChatOpenAI
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
import os
os.environ["OPENAI_API_BASE"] = "http://192.168.100.111:9997/v1"
os.environ["OPENAI_API_KEY"] = "dummy"

table_info = """

        Database:
        ------
        Build a predicate sentence:
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


    请注意!下面有序列表中提到的信息极为关键！请参考列表中的内容编写SQL：
    1.表中xl字段中的内容仅会有"本科毕业生"、"本科生毕业"、"专科生毕业"、"专科毕业生"这四种类型!
    2.长理是长沙理工大学的简称!当用户想查询长理相关内容时，其实是查询长沙理工大学的相关内容！
      例如：当用户提问请你查询表中长理的学生人数,SQL语句应为：
      ```SQL
      SELECT COUNT(*) AS '长理学生人数'
      FROM dw_s_employment
      WHERE xxmc = '长沙理工大学';
      ```SQL
)
"""


template = '''
Given an input question, first create a syntactically correct {dialect} query to run, then look at the results of the query and return the answer.
Use the following format:

Question: "Question here"
SQLQuery: "SQL Query to run"
SQLResult: "Result of the SQLQuery"
Answer: "Final answer here"

Only use the following tables:

{table_info}.

Question: {input}


top_k = {top_k}

'''
prompt = PromptTemplate.from_template(template)


answer_prompt = PromptTemplate.from_template(
    """Given the following user question, corresponding SQL query, and SQL result, answer the user question.
    Question: {question}
    SQL Query: {query}
    SQL Result: {result}
    Answer: """
)

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

llm = ChatOpenAI(model="qwen2", max_tokens=5000, max_retries=2)

write_query = create_sql_query_chain(llm, db, prompt=prompt)

print("生成的SQL为：", write_query.invoke(
    {"question": "查询云就业大学就业数据", "table_info": table_info}))

execute_query = QuerySQLDataBaseTool(db=db)

chain = (
    RunnablePassthrough.assign(query=write_query).assign(
        result=itemgetter("query") | execute_query
    )
    | answer_prompt
    | llm
    | StrOutputParser()
)

response = chain.invoke({"question": "查询20条云就业大学就业数据"})

print(response)

# chain = write_query | execute_query
# response = chain.invoke(
#    {"question": "请你查询表中所有专科生毕业或专科毕业生的人数"})
# print(response)
