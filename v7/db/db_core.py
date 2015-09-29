#!/usr/bin/env python
# -*-coding:utf8-*-

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

    def query(self, sql):
        cur = self.newcursor()
        cur.execute(sql)
        return cur

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