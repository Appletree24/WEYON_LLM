import os
from unittest import TestCase
from logs import get_logger


class Test(TestCase):

    def test_get_logger(self):
        log = get_logger('test_get_logger')
        self.assertIsNotNone(log)

    def test_logger_output(self):
        log = get_logger('test_logger_output')
        log.info('test')

    def test_get_logger_with_output_file(self):
        self.assertFalse(os.path.exists('test.log'))
        log = get_logger('test', output_file='test.log')
        self.assertIsNotNone(log)
        log.info('test_get_logger_with_output_file')
        self.assertTrue(os.path.exists('test.log'))
        # Delete the file
        os.remove('test.log')
