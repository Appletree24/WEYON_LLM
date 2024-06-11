from RAG.history_chat import HistoryChatRAG
import sys
import os

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if project_root not in sys.path:
    sys.path.append(project_root)


docx_path = "WEYON_LLM/dataFiles/湖南科技大学2022届毕业生就业质量年度报告12.31.docx"

# 问题回答System模板
qa_system_prompt = """
你是一名大学就业处指导老师，使用如下的信息去回答问题，\
如果你不知道准确的答案，请说“私密马赛，我不知道”。\
最多使用五句话来回答，并且保持回答的准确性。\

{context}
"""

if __name__ == '__main__':
    advisor = HistoryChatRAG(model_name="thenlper/gte-large", openai_api_key="xxx",
                             openai_api_base="http://192.168.100.111:8000/v1/", qa_system_prompt=qa_system_prompt)

    advisor.load_file_and_chunk(
        docx_path=docx_path, chunk_size=1024, chunk_overlap=128, persist_directory="db")

    query_1 = "湖南科技大学2022届毕业生初次毕业去向落实率为84.58%，其中灵活就业率仅为9.14%。评价一下2022年的湖南科技大学毕业生质量高低水平"

    answer_1 = advisor.completion(5, query_1)
    print(answer_1)

    query_2 = "湖南科技大学2022届本科毕业生的灵活就业率是多少？"

    answer_2 = advisor.completion(5, query_2)

    print(answer_2)
