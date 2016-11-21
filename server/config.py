from configparser import ConfigParser
from flask import request
from urllib.parse import urljoin
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker, Session
from lib.client import Client


class Config:
    def __init__(self):
        self.cfg = ConfigParser()
        self.cfg.read("server.conf")

        self._mysql = None
        self._session_maker = None
        self._api = None

    @property
    def mysql(self) -> Engine:
        """
        Get connection to MySQL database.
        :return: MySQLWrapper encapsulating MySQLConnection.
        """
        if self._mysql is None:
            sql_config = self.cfg["mysql"]
            self._mysql = create_engine("mysql+mysqlconnector://%s:%s@%s/%s?charset=%s" % (
                sql_config.get("User", "root"),
                sql_config.get("Password", ""),
                sql_config.get("Host", "localhost"),
                sql_config.get("Database", "mon"),
                sql_config.get("Charset", "utf8")
            ), pool_recycle=3600)

        return self._mysql

    def session(self) -> Session:
        if self._session_maker is None:
            self._session_maker = sessionmaker(bind=self.mysql)

        return self._session_maker()

    @property
    def api(self) -> Client:
        if self._api is None:
            self._api = Client(urljoin(request.url_root, self.cfg.get("api", "Address", fallback="/")))

        return self._api


config = Config()
