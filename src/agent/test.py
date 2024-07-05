# import json
# table_names = '{"tables": ["dw_s_employment"]}'
# json_data = json.loads(table_names)
# if 'tables' in json_data:
#     table_names = json_data['tables']
#     print(1, table_names)
# elif 'table_names' in json_data:
#     table_names = json_data['table_names']
#     print(2)
# print(type(table_names),table_names[0])
# if isinstance(table_names, list):
#     table_names = table_names[0]
#
# print(json_data['tables'])
# 插入产品信息
sql = {"query": "SELECT * FROM dw_s_employment WHERE xxmc = '云就业大学'"}