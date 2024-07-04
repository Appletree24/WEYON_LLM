# 暂时没琢磨出来怎么接入，文件会报错


# from vanna.remote import VannaDefault
# vn = VannaDefault(model='chinook', api_key='e85b976e13f940868ef53b9129ffdaf0')
# vn.connect_to_sqlite('https://vanna.ai/Chinook.sqlite')
# vn.ask('What are the top 10 artists by sales?')
#
# from vanna.flask import VannaFlaskApp
# VannaFlaskApp(vn).run()

from vanna.openai import OpenAI_Chat
from vanna.chromadb import ChromaDB_VectorStore
from openai import OpenAI

client = OpenAI(
    api_key='dummy',
    base_url='http://192.168.100.111:9997/v1',
    default_headers={"x-foo": "true"}
)


class MyVanna(ChromaDB_VectorStore, OpenAI_Chat):
    def __init__(self, config=None):
        # ChromaDB_VectorStore.__init__(self, config)
        OpenAI_Chat.__init__(self, config)


vn = MyVanna(config={
    'client': client
})

print("1")
