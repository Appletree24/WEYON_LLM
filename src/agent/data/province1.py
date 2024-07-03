# name: province1.py
# description: 处理用户输入的文本相关信息——相似度的方式
# author: acxgdxy
# time: 2024/07/02
import re
from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from modelscope.models import Model


class Province1:
    def __init__(self):
        self.text = [
            "北京市", "天津市", "上海市", "重庆市",
            "河北省", "山西省", "辽宁省", "吉林省", "黑龙江省",
            "江苏省", "浙江省", "安徽省", "福建省", "江西省",
            "山东省", "河南省", "湖北省", "湖南省", "广东省",
            "海南省", "四川省", "贵州省", "云南省", "陕西省",
            "甘肃省", "青海省", "台湾省", "内蒙古自治区", "广西壮族自治区",
            "西藏自治区", "宁夏回族自治区", "新疆维吾尔自治区", "香港特别行政区", "澳门特别行政区"
        ]
        self.model_id = "iic/nlp_gte_sentence-embedding_chinese-base"
        self.pipeline_se = pipeline(
            Tasks.sentence_embedding,
            model=self.model_id,
            sequence_length=512)

    # 使用正则表达式提取并替换引号之间的值
    def replace_quoted_values(self, sql, new_value='', n=1):
        count = 0

        # 替换引号之间的值
        def replace_match(match):
            nonlocal count
            count += 1
            if count == n:
                return f"'{new_value}'"
            return match.group(0)

        # 使用正则表达式进行替换
        pattern = re.compile(r"'(.*?)'")
        matches = pattern.findall(sql)
        for i in range(len(matches)):
            data = self.search(matches[i])
            if data[1] == 1:
                new_value = data[0]
                n = i + 1
                sql = pattern.sub(replace_match, sql)
                count = 0
                # print(new_value, n, sql, count)

        return sql

    def search(self, para):
        data = [para]
        print(data)
        inputs = {
            "source_sentence": data,
            "sentences_to_compare": self.text
        }
        result = self.pipeline_se(inputs)
        max = 0
        index = 0
        # 如果是与这些城市一定都不相关的话，则产生的相似度值基本都不会超过0.5
        threshold = 0.5
        flag = 0
        scores = result['scores']
        for i in range(len(scores)):
            if max < scores[i]:
                max = scores[i]
                index = i
            # 设置阈值
            if scores[i] > threshold:
                flag = 1
        return self.text[index], flag


if __name__ == "__main__":
    p = Province1()
    result = p.replace_quoted_values(
        sql="SELECT * FROM dw_s_employment_company WHERE xxcs = '湖南' AND lsbyqx = '湖北'")
    print(result)
