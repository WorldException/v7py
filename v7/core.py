#!/usr/bin/env python
# -*-coding:utf8-*-
from v7 import query_translator, md_reader, mylog
import os
class Application:
    '''
    Хранилище метаданных и методы для работы с 1С базой
    '''
    def __init__(self, base_path=None):
        mylog.debug('init Application')
        self.metadata = None
        self.md = None
        self.db = None
        self.load_folder(base_path)

    def load_folder(self, path):
        self.base_path = path
        self.path_md = ''
        self.path_dba = ''
        self.db_server, self.db_name, self.db_user, self.db_password = '', '', '', ''
        if os.path.isdir(self.base_path):
            mylog.debug(' init from folder: %s' % self.base_path)
            self.path_md  = os.path.join(self.base_path, '1Cv7.MD')
            self.path_dba = os.path.join(self.base_path, '1Cv7.DBA')
            if os.path.exists(self.path_md):
                self.load_1cv7_md(self.path_md)
            if os.path.exists(self.path_dba):
                from v7 import dba
                self.db_server, self.db_name, self.db_user, self.db_password = dba.read_dba(self.path_dba)
                self.init_db_engine()

    def init_db_engine(self):
        if self.db_server:
            mylog.debug('init MSSQL connection proxy')
            from v7 import MS_Proxy
            self.db = MS_Proxy(self.db_name, self.db_server, self.db_user, self.db_password)

    def connect(self):
        if self.db:
            mylog.debug('connect db')
            self.db.connect()

    def disconect(self):
        if self.db:
            mylog.debug('disconect db')
            self.db.close()

    @property
    def connected(self):
        if self.db:
            return self.db.connected()
        return False

    def load_1cv7_md(self,filename):
        mylog.debug(' load: %s' % filename)
        self.md = md_reader.parse_md(filename)
        self.metadata = md_reader.extract_metadata(self.md)

    def setDatabase(self, db):
        self.db = db

    def query(self, sqltext):
        if self.db:
            if not self.db.connected:
                self.db.connect()
            return self.db.query(self.prepare_query(sqltext))
        return None

    def prepare_query(self, sqltext):
        sql = query_translator.prepareSQL(sqltext, self.metadata)
        return sql
