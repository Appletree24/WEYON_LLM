import os
from langchain_openai import ChatOpenAI
import utils.config_util as utils
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

utils.load_config()
if str(utils.tavily_api_key) != '':
    os.environ["TAVILY_API_KEY"] = utils.tavily_api_key
os.environ["OPENAI_API_KEY"] = utils.key_gpt_api_key
os.environ["OPENAI_API_BASE"] = utils.gpt_base_url
# 创建llm
llm = ChatOpenAI(model=utils.gpt_model_engine)
# 保存基本信息到记忆
utils.load_config()
print(llm.invoke("请将一下数据处理为markdown格式："
                 "666666,666666,云就业大学,湖南省,长沙市,本科,普通本科高校,综合类院校,2021届"
                 "666666,666666,云就业大学,湖南省,长沙市,本科,普通本科高校,综合类院校,2023届"
                 "666666,666666,云就业大学,湖南省,长沙市,本科,普通本科高校,综合类院校,2023届"
                 "666666,666666,云就业大学,湖南省,长沙市,本科,普通本科高校,综合类院校,2023届"
                 "666666,666666,云就业大学,湖南省,长沙市,本科,普通本科高校,综合类院校,2022届"
                 "666666,666666,云就业大学,湖南省,长沙市,本科,普通本科高校,综合类院校,2022届"
                 "666666,666666,云就业大学,湖南省,长沙市,本科,普通本科高校,综合类院校,2021届"
                 "666666,666666,云就业大学,湖南省,长沙市,本科,普通本科高校,综合类院校,2023届"
                 "666666,666666,云就业大学,湖南省,长沙市,本科,普通本科高校,综合类院校,2023届"))
