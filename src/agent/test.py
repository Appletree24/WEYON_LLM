import re

# 示例SQL查询
sql_query = "SELECT * FROM dw_s_employment_company WHERE xxcs = '长沙市' AND lsbyqx = '是'"

# 使用正则表达式提取并替换第一个引号之间的值
def replace_first_quoted_value(query, new_value):
    # 定义计数器
    count = 0

    # 替换引号之间的值
    def replace_match(match):
        nonlocal count
        count += 1
        if count == 1:
            return f"'{new_value}'"
        return match.group(0)

    # 使用正则表达式进行替换
    pattern = re.compile(r"'(.*?)'")
    result = pattern.sub(replace_match, query, count=1)
    return result

# 调用函数，替换第一个引号之间的值为 "新值"
new_sql_query = replace_first_quoted_value(sql_query, "新值")
print("替换后的SQL查询:", new_sql_query)
