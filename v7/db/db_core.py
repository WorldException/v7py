#!/usr/bin/env python
# -*-coding:utf8-*-
import logging
mylog = logging.getLogger(__name__)

options = {
    'host':'',
    'port':'',
    'user':'',
    'password':''
}

class DB_Proxy:

    def __init__(self,database, host, user='', password='', port=''):
        self.cnx = None
        self.host = host
        self.user = user
        self.password = password
        self.port = port
        self.database = database

    def _after_init(self):
        pass

    def connect(self):
        pass

    def query(self, sql, reconect=True):
        try:
            cur = self.newcursor()
            cur.execute(sql)
            return cur
        except Exception as e:
            if e.args[0] == '08S01' and reconect:
                # ошибка подключения, попробовать переподключитсья
                mylog.warning(u'Потеряно подключение к серверу {0}, попытка переподключиться'.format(self.host))
                self.connect()
                return self.query(sql, reconect=False)
            else:
                raise e

    def newcursor(self):
        if self.cnx is None:
            self.connect()
        return self.cnx.cursor()

    def close(self):
        if self.cnx:
            self.cnx.close()
            self.cnx = None

    def connected(self):
        if self.cnx:
            return self.cnx.connected == 1
        return False