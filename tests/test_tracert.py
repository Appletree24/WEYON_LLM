from unittest import TestCase
from unittest.mock import MagicMock

from logs import tracert


class Test(TestCase):
    def test_input(self):
        tracert.logger.info = MagicMock("logger")

        @tracert.input
        def sum(a, b):
            return a + b

        self.assertEqual(sum(1, 2), 3)
        tracert.logger.info.assert_called_once_with('Function sum called with args: (1, 2) and kwargs: {}')

    def test_output(self):
        tracert.logger.info = MagicMock("logger")

        @tracert.output
        def sum(a, b):
            return a + b

        self.assertEqual(sum(1, 2), 3)
        tracert.logger.info.assert_called_once_with('Function sum returned: 3')

    def test_time(self):
        tracert.logger.info = MagicMock("logger")

        @tracert.time
        def sum(a, b):
            return a + b

        self.assertEqual(sum(1, 2), 3)
        tracert.logger.info.assert_called()
