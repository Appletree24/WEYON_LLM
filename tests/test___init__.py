from unittest import TestCase
from retriever.redisdb import RedisStore


class TestRedisStore(TestCase):
    red = RedisStore(host="192.168.100.111", port=6379, db=0)

    def test_mset(self):
        self.red.mset({"a": "b", "c": "d"})
        self.assertEqual(["b"], self.red.mget("a"))
        self.red.mdelete(["a", "c"])

    def test_mdelete(self):
        self.red.mset({"a": "b", "c": "d"})
        self.red.mdelete(["a", "c"])
        self.assertEqual(self.red.mget(["a"]), [None])

    def test_yield_keys(self):
        self.red.mset({"a": "b", "c": "d"})
        self.assertEqual(["a", "c"], self.red.yield_keys())
        self.red.mdelete(["a", "c"])

    def test_mget(self):
        self.red.mset({"a": "b", "c": "d"})
        self.assertEqual(["b", "d"], self.red.mget(["a", "c"]))
        self.red.mdelete(["a", "c"])
