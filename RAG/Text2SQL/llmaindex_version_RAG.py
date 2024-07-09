from sqlalchemy import text, insert, create_engine, MetaData, Table, Column, String, Integer, select
from llama_index.core import SQLDatabase
from typing import List
import ast
from modelscope_embedding import ModelScopeEmbeddings
from llama_index.core import ServiceContext, set_global_service_context, ListIndex, Document
from llama_index.core.base.llms.types import ChatMessage
from llama_index.core.query_engine import NLSQLTableQueryEngine
from llama_index.llms.openai_like import OpenAILike

rows = [
    # iPhone13 Reviews
    {"id": 1, "category": "Phone", "product_name": "Iphone13", "review": "The iPhone13 is a stellar leap forward. From its sleek design to the crystal-clear display, it screams luxury and functionality. Coupled with the enhanced battery life and an A15 chip, it's clear Apple has once again raised the bar in the smartphone industry."},
    {"id": 2, "category": "Phone", "product_name": "Iphone13",
        "review": "This model brings the brilliance of the ProMotion display, changing the dynamics of screen interaction. The rich colors, smooth transitions, and lag-free experience make daily tasks and gaming absolutely delightful."},

    {"id": 3, "category": "Phone", "product_name": "Iphone13",
        "review": "The 5G capabilities are the true game-changer. Streaming, downloading, or even regular browsing feels like a breeze. It's remarkable how seamless the integration feels, and it's obvious that Apple has invested a lot in refining the experience."},

    # SamsungTV Reviews
    {"id": 4, "category": "TV", "product_name": "SamsungTV", "review": "Samsung's display technology has always been at the forefront, but with this TV, they've outdone themselves. Every visual is crisp, the colors are vibrant, and the depth of the blacks is simply mesmerizing. The smart features only add to the luxurious viewing experience."},
    {"id": 5, "category": "TV", "product_name": "SamsungTV",
        "review": "This isn't just a TV; it's a centerpiece for the living room. The ultra-slim bezels and the sleek design make it a visual treat even when it's turned off. And when it's on, the 4K resolution delivers a cinematic experience right at home."},
    {"id": 6, "category": "TV", "product_name": "SamsungTV",
        "review": "The sound quality, often an oversight in many TVs, matches the visual prowess. It creates an enveloping atmosphere that's hard to get without an external sound system. Combined with its user-friendly interface, it's the TV I've always dreamt of."},

    # Ergonomic Chair Reviews
    {"id": 7, "category": "Furniture", "product_name": "Ergonomic Chair",
        "review": "Shifting to this ergonomic chair was a decision I wish I'd made earlier. Not only does it look sophisticated in its design, but the level of comfort is unparalleled. Long hours at the desk now feel less daunting, and my back is definitely grateful."},
    {"id": 8, "category": "Furniture", "product_name": "Ergonomic Chair",
        "review": "The meticulous craftsmanship of this chair is evident. Every component, from the armrests to the wheels, feels premium. The adjustability features mean I can tailor it to my needs, ensuring optimal posture and comfort throughout the day."},
    {"id": 9, "category": "Furniture", "product_name": "Ergonomic Chair",
        "review": "I was initially drawn to its aesthetic appeal, but the functional benefits have been profound. The breathable material ensures no discomfort even after prolonged use, and the robust build gives me confidence that it's a chair built to last."},
]

engine = create_engine("sqlite:///:memory:")


# Define the embedding model to be used
embedding_model = "jinaai/jina-embeddings-v2-base-zh"

embeedings = ModelScopeEmbeddings(
    modelscope_embeddings_model_id=embedding_model)

llm = OpenAILike(model="qwen2", api_base="http://192.168.100.111:9997/v1",
                 api_key="dummy", max_tokens=5000)

metadata_obj = MetaData()

table_name = "product_reviews"

product_reviews_table = Table(
    table_name,
    metadata_obj,
    Column("id", Integer(), primary_key=True),
    Column("category", String(16), primary_key=True),
    Column("product_name", Integer),
    Column("review", String(16), nullable=False)
)

metadata_obj.create_all(engine)

sql_database = SQLDatabase(engine, include_tables=["product_reviews"])

for row in rows:
    stmt = insert(product_reviews_table).values(**row)
    with engine.connect() as connection:
        cursor = connection.execute(stmt)
        connection.commit()


service_context = ServiceContext.from_defaults(embed_model=embeedings, llm=llm)
set_global_service_context(service_context)


def generate_questions(user_query: str) -> List[str]:
    system_message = '''
  You are given with Postgres table with the following columns.

  city_name, population, country, reviews.

  Your task is to decompose the given question into the following two questions.

  1. Question in natural language that needs to be asked to retrieve results from the table.
  2. Question that needs to be asked on the top of the result from the first question to provide the final answer.

  Example:

  Input:
  How is the culture of countries whose population is more than 5000000

  Output:
  1. Get the reviews of countries whose population is more than 5000000
  2. Provide the culture of countries
  '''

    messages = [
        ChatMessage(role="system", content=system_message),
        ChatMessage(role="user", content=user_query),
    ]
    generated_questions = llm.chat(messages).message.content.split('\n')

    return generated_questions[0], generated_questions[1]


user_query = "What are the reviews of the products with the category 'Laptop'?"

text_to_sql_query, rag_query = generate_questions(user_query)

print("本次生成的text_to_sql_query是", text_to_sql_query)
print("本次生成的rag_query是", rag_query)

sql_query_engine = NLSQLTableQueryEngine(
    sql_database=sql_database,
    tables=["product_reviews"],
    llm=llm,
    synthesize_response=False
)

# ATTENTION：sql_query_engine下的query方法好像必须用这种外部传参的形式，不然会报错，暂时没研究清楚

sql_response = sql_query_engine.query(text_to_sql_query)

print("本次查询生成的SQL是", sql_response.metadata['sql_query'])

sql_response_list = ast.literal_eval(sql_response.response)
text = [' '.join(t) for t in sql_response_list]
text = ' '.join(text)

listindex = ListIndex([Document(text=text)])
list_query_engine = listindex.as_query_engine()
response = list_query_engine.query(rag_query)

print(response.response)


def pipe_line(user_query: str) -> str:
    text_to_sql_query, rag_query = generate_questions(user_query)

    sql_response = sql_query_engine.query(text_to_sql_query)
    sql_response_list = ast.literal_eval(sql_response.response)

    text = [' '.join(t) for t in sql_response_list]
    text = ' '.join(text)

    listindex = ListIndex([Document(text=text)])
    list_query_engine = listindex.as_query_engine()

    final_response = list_query_engine.query(rag_query)

    return final_response.response
