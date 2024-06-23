from unittest import TestCase


class TestConfigurationContext(TestCase):

    def test_parse(self):
        """
        测试配置上下文的参数解析
        """
        from basic import ConfigurationContext

        context = ConfigurationContext('../resources/application.yaml')

        self.assertEqual(context['serve_chat_model_config']['openai_api_base']
                         , "http://192.168.100.111:9997/v1")
