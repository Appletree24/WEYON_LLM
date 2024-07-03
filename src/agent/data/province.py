# name: province.py
# description: 处理用户输入的文本相关信息
# author: acxgdxy
# time: 2024/07/02
import re


class ProvinceData:
    # 中国各省、自治区、直辖市和特别行政区列表
    regions = {
        "北京": "北京市", "天津": "天津市", "上海": "上海市", "重庆": "重庆市",
        "河北": "河北省", "山西": "山西省", "辽宁": "辽宁省", "吉林": "吉林省", "黑龙江": "黑龙江省",
        "江苏": "江苏省", "浙江": "浙江省", "安徽": "安徽省", "福建": "福建省", "江西": "江西省",
        "山东": "山东省", "河南": "河南省", "湖北": "湖北省", "湖南": "湖南省", "广东": "广东省",
        "海南": "海南省", "四川": "四川省", "贵州": "贵州省", "云南": "云南省", "陕西": "陕西省",
        "甘肃": "甘肃省", "青海": "青海省", "台湾": "台湾省",
        "内蒙古": "内蒙古自治区", "广西": "广西壮族自治区", "西藏": "西藏自治区", "宁夏": "宁夏回族自治区",
        "新疆": "新疆维吾尔自治区",
        "香港": "香港特别行政区", "澳门": "澳门特别行政区"
    }
    # 将省份名转换为正则表达式
    province_pattern = re.compile("|".join(regions.keys()))

    def __init__(self):
        pass

    def replace_region(self, text):
        def replace_match(match):
            region = match.group(0)
            full_name = ProvinceData.regions[region]
            # 如果匹配到的区域后面没有正确的后缀，则添加后缀
            if not text[text.index(region) + len(region):].startswith(full_name[len(region):]):
                return full_name
            return region

        # 使用正则表达式进行替换
        result = ProvinceData.province_pattern.sub(replace_match, text)
        return result


if __name__ == '__main__':
    # 测试文本
    text = "我最近去了北京和湖南，还计划去上海和广东。内蒙古是一个美丽的地方。"
    # 调用函数
    province = ProvinceData()
    result = province.replace_region(text)
    print(result)
