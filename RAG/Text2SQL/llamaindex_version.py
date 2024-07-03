#!//home/kemove/miniconda3/envs/rag_zzh/lib/ python3.11.0
# -*- coding:utf-8 -*-
# @FileName  :llamaindex_version.py
# @Time      :2024/07/03 15:42:20
# @Author    :Appletree24
# @Email     :1246908638zxc@gmail.com
# @Software  :Vscode
# @Description: llamaindex版本的Text2SQL，没有使用Agent形式
# @Version   :1.0
# 请不要用GPT生成代码中的注释，谢谢。

from llama_index.core.query_engine import RetrieverQueryEngine
from llama_index.core.response.notebook_utils import display_source_node
from llama_index.core.retrievers import NLSQLRetriever
from llama_index.core import VectorStoreIndex
from llama_index.core import SQLDatabase
from llama_index.core.objects import (
    SQLTableNodeMapping,
    ObjectIndex,
    SQLTableSchema,
)
from llama_index.core.indices.struct_store.sql_query import (
    SQLTableRetrieverQueryEngine,
)
from llama_index.core.query_engine import NLSQLTableQueryEngine

# Import necessary modules from SQLAlchemy for database creation and manipulation
from sqlalchemy import text, insert, create_engine, MetaData, Table, Column, String, Integer, select

# Import the OpenAILike model for Natural Language processing
from llama_index.llms.openai_like import OpenAILike

# Define the embedding model to be used
embedding_model = "iic/nlp_gte_sentence-embedding_chinese-base"

# Initialize the LLM with model details and API configuration
llm = OpenAILike(model="qwen2", api_base="http://192.168.100.111:9997/v1",
                 api_key="dummy", max_tokens=100)

# Create an in-memory SQLite database engine
engine = create_engine("sqlite:///:memory:")
metadata_obj = MetaData()

# Define the city_stats table schema with columns for city name, population, and country
table_name = "city_stats"
city_stats_table = Table(
    table_name,
    metadata_obj,
    Column("city_name", String(16), primary_key=True),
    Column("population", Integer),
    Column("country", String(16), nullable=False),
)
# Create the table in the database
metadata_obj.create_all(engine)

# Create an SQLDatabase object including the city_stats table
sql_database = SQLDatabase(engine, include_tables=["city_stats"])

# Define rows of data to be inserted into the city_stats table
rows = [
    {"city_name": "Toronto", "population": 2930000, "country": "Canada"},
    {"city_name": "Tokyo", "population": 13960000, "country": "Japan"},
    {"city_name": "Chicago", "population": 2679000, "country": "United States"},
    {"city_name": "Seoul", "population": 9776000, "country": "South Korea"},
]

# Insert the defined rows into the city_stats table
for row in rows:
    stmt = insert(city_stats_table).values(**row)
    with engine.begin() as connection:
        cursor = connection.execute(stmt)

# Select and display the current contents of the city_stats table
stmt = select(
    city_stats_table.c.city_name,
    city_stats_table.c.population,
    city_stats_table.c.country,
).select_from(city_stats_table)

with engine.connect() as connection:
    results = connection.execute(stmt).fetchall()
    print(results)

# Optional pre-query to display city names in the city_stats table
with engine.connect() as con:
    rows = con.execute(text("SELECT city_name from city_stats"))
    for row in rows:
        print(row)

# Create an NLSQLTableQueryEngine for natural language SQL querying
query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database, tables=["city_stats"], llm=llm
)
query_str = "Which city has the highest population?"
print(query_engine.query(query_str))

# Create a SQLTableNodeMapping for the SQL database
table_node_mapping = SQLTableNodeMapping(sql_database)

# Define SQLTableSchema objects for each table in the database
table_schema_objs = [
    SQLTableSchema(table_name="city_stats")
]

# Create an ObjectIndex from the table schemas and mapping, using VectorStoreIndex
obj_index = ObjectIndex.from_objects(
    table_schema_objs,
    table_node_mapping,
    VectorStoreIndex,
)

# Create a SQLTableRetrieverQueryEngine for retrieving query results
query_engine = SQLTableRetrieverQueryEngine(
    sql_database, obj_index.as_retriever(similarity_top_k=1)
)

# Execute a query to find the city with the highest population
response = query_engine.query("Which city has the highest population?")
print(response)

# Create an NLSQLRetriever for natural language SQL retrieval with raw results
nl_sql_retriever = NLSQLRetriever(
    sql_database, tables=["city_stats"], return_raw=True
)

# Create a RetrieverQueryEngine using the NLSQLRetriever
query_engine = RetrieverQueryEngine.from_args(nl_sql_retriever)

# Execute a query to get the top 5 cities by population
response = query_engine.query(
    "Return the top 5 cities (along with their populations) with the highest population."
)

# Print the query response
print(str(response))
