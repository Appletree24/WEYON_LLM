# name: fay_agent.py
# description: 以表格形式输出
# author: woshixiong,acxgdxy
# time: 2024/07/03
# 请不要用GPT生成代码中的注释，谢谢。
import os
from agent.globalData import globalData

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
globalData._init()


class DataTreating:
    def data_to_markdown(self, input_string: str):
        print("2", input_string)
        if input_string is None or input_string == '' or 'Error:' in input_string:
            return
        file_path = os.path.join(BASE_DIR, 'answer.txt')
        with open(file_path, 'w', encoding='UTF-8') as file:
            file.write('false\n')
        clean_string = input_string.replace("[", "").replace("]", "").replace("'", "")
        items = clean_string.split("), (")

        header_items = items[0].replace("(", "").replace(")", "").split(", ")
        header = "| " + " | ".join([f"字段{i + 1}" for i in range(len(header_items))]) + " |\n"
        separator = "| " + " | ".join(["---"] * len(header_items)) + " |\n"

        markdown_table = header + separator

        for item in items:
            item = item.replace("(", "").replace(")", "")
            fields = item.split(", ")
            markdown_table += "| " + " | ".join(fields) + " |\n"
        with open(file_path, 'r+', encoding='UTF-8') as file:
            lines = file.readlines()
            lines[0] = 'true\n'
            lines.append(markdown_table)
            file.seek(0)
            file.writelines(lines)
        globalData.set_value('markdown_table', markdown_table)
