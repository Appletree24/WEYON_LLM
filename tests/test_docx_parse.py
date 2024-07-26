import os.path
from unittest import TestCase

from kb.docx_parse import DocxLoader


class TestDocxLoader(TestCase):
    def test_parse_to_tree(self):
        # 检测是否存在测试u文件
        file_path = '【测试用例】湖南大众传媒职业技术学院2023届毕业生就业质量年度报告.docx'
        if not os.path.exists(file_path):
            raise FileNotFoundError(f'【{file_path}】 测试文件文件不存在，请检查文件路径是否正确。')
        doc = DocxLoader(file_path)
        for e in doc:
            print(e.get_value_from_tree(), end='\n' + '-' * 100 + '\n\n')
        self.assertIsNotNone(doc)
