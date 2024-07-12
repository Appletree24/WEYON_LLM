from typing import Sequence, List, Optional, Union, Iterator, Tuple

from langchain_core.stores import BaseStore, K, V
import redis


class RedisStore(BaseStore):
    """Store that uses Redis as the underlying storage."""

    def __init__(self, host, port, db, username=None, password=None):
        """Initialize the RedisStore.
        Args:
            host (str): The host of the Redis server.
            port (int): The port of the Redis server.
            db (int): The database index to use.
            username (str, optional): The username to use for authentication. Defaults to None.
            password (str, optional): The password to use for authentication. Defaults to None.
        """

        self.pool = redis.ConnectionPool(host=host, port=port, db=db, username=username, password=password,
                                         decode_responses=True)
        self.db = db
        self.redis = redis.Redis(connection_pool=self.pool)
        self.redis.ping()

    def mset(self, key_value_pairs: Sequence[Tuple[K, V]]) -> None:
        self.redis.mset(dict(key_value_pairs))

    def mdelete(self, keys: Sequence[K]) -> None:
        self.redis.delete(*keys)

    def yield_keys(self, *, prefix: Optional[str] = None) -> Union[Iterator[K], Iterator[str]]:
        return self.redis.scan(cursor=self.db, match=prefix or '*')[1]

    def mget(self, keys: Sequence[K]) -> List[Optional[V]]:
        return self.redis.mget(keys)
