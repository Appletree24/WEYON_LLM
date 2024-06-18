import pandas as pd
import os


class DBConfig:
    host = 'db_host'
    port = 3306
    user = 'username'
    password = 'password'


class SqlMapper:
    def __init__(self, host=DBConfig.host, port=DBConfig.port, user=DBConfig.user, password=DBConfig.password,
                 sup_path=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password

        self.conn = None
        if sup_path:
            self.sup_path = os.path.normpath(sup_path)
        else:
            self.sup_path = None

    def __enter__(self):
        import pymysql
        self.conn = pymysql.connect(host=self.host,
                                    port=self.port,
                                    user=self.user,
                                    password=self.password)
        return self

    def query(self, sql) -> pd.DataFrame:
        """
        执行sql语句，并返回查询结果
        :param sql: sql语句
        :return: 返回查询结果
        """
        res = pd.read_sql(sql, self.conn)
        return res

    def query_and_save(self, sql, path):
        """
        执行sql语句，并保存结果到文件
        :param sql: sql语句
        :param path: 保存路径
        :return: 返回保存的绝对路径和查询结果
        """
        res = self.query(sql)
        path = self.save(res, path)
        return path, res

    @staticmethod
    def __is_parent_path(parent_path, path):
        return os.path.normpath(parent_path) in os.path.normpath(path)

    def __append_path(self, path):
        path = os.path.normpath(path)
        if self.sup_path:
            if not self.__is_parent_path(self.sup_path, path):
                raise Exception("path is not under sup_path")
            path = os.path.join(self.sup_path, path)

        return path

    def save(self, result: pd.DataFrame, path: str):
        """
        查询结果保存到文件
        :param result: 查询结果
        :param path: 保存路径
        :return: 保存路径的绝对路径
        """
        # 如果sup_path不为空，最终路径保存在sup_path路径之下
        if self.sup_path:
            path = self.__append_path(path)
        # 保存到csv文件
        if not os.path.exists(path):
            os.makedirs(path)
        if os.path.exists(path) and os.path.isdir(path):
            # 删除该空目录
            os.rmdir(path)

        result.to_csv(path, index=False)
        return os.path.abspath(path)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.close()


# usage
if __name__ == '__main__':
    sql = "SELECT * FROM ai_use.dw_s_employment"
    with SqlMapper() as sm:
        path, df = sm.query_and_save(sql, 'data/out/dw_s_employment.csv')
    df
