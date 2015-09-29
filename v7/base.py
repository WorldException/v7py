#!/usr/bin/env python
#-*-coding:utf8-*-

#!/usr/bin/env python
#-*-coding:utf8-*-
import logging
mylog = logging.getLogger('v7.base')
from v7.query_translator import prepareSQL
import os

#from v7.config import Work

def date_param(datetimeparam, end_modificator=False):
    s = datetimeparam.strftime('%Y%m%d')
    if end_modificator:
        s=s+'Z'
    return "'%s'" % s


class Base:
    """
    это главный класс для работы с базой данных, передаем конфиг и можем вызвать запросы
    """
    config = None

    def __init__(self, config=None):
        if config:
            self.config = config
        if self.config is None:
            raise RuntimeError('config for v7 is Null')
        if not config.PATH_1Cv7_MD:
            config()  # инициализация конфига если забыли
        # Если нет конфига то скачиваю
        if not os.path.exists(config.PATH_1Cv7_MD):
            self.download()
        #ToDo если конфиг файл старый то надо бы обновить
        self.read_config()
        self.prepare_connection()

    def download(self):
        # обновленияе 1с-ых файлов
        self.config.update_meta_files()

    def read_config(self):
        # загрузка конфигурации
        from v7 import md_reader2
        self.reader = md_reader2.MdReader(self.config.PATH_1Cv7_MD).read()
        self.metadata = self.reader.MdObject

    def prepare_connection(self):
        # подготовка подключения
        from v7 import dba
        self.dba_info = dba.read_dba(self.config.PATH_1Cv7_DBA, True)
        mylog.info('DBA: %s' % repr(self.dba_info))
        from v7.db import mssql
        self.connection = mssql.MS_Proxy(self.dba_info['DB'], self.dba_info['Server'], self.dba_info['UID'], self.dba_info['PWD'])

    def query(self, sql):
        return Query(sql, self)

    def add_query(self, **kwargs):
        """
        добавить метод запрос
        """
        pass

class Query:
    """
    объект запроса, объединяет транслятор и выполение запроса
    """
    def __init__(self, sql, parent):
        self.sql = sql # свойство или переменная?
        self._sql_v7_=''
        self.params = {}
        self.parent = parent

    def set_param(self, name, value):
        """
        :param name: name_ означает что используется модификатор как в 1С++ ~ для обозначения даты конец дня
        :param value:
        :return:
        """
        modificator = name.endswith('_')
        if modificator:
            name = name[:-1]
        if str(type(value)) == "<type 'datetime.datetime'>":
            self.params[name] = date_param(value, modificator)
        else:
            self.params[name] = value

    def set_params(self, **kwargs):
        for key, value in kwargs.items():
            self.set_param(key, value)

    @property
    def sql(self):
        return self._sql_

    @sql.setter
    def sql(self, value):
        self._sql_v7_ = ''
        self._sql_ = value

    @property
    def v7(self):
        if not self._sql_v7_:
            self._sql_v7_ = prepareSQL(self.sql, self.parent.metadata)
        return self._sql_v7_ % self.params

    def __unicode__(self):
        return u"SQL:\n%s\nV7\n%s" % (self.sql, self.v7)

    def __str__(self):
        return self.__unicode__().decode('utf8')

    def __call__(self, *args, **kwargs):
        return self.parent.connection.query(self.v7.encode('cp1251'))


def test():
    from db_work import WorkDev
    db = Base(WorkDev)
    q = db.query(u'select top 10 d.#ХарактеристикаТовара from $Документ.#Уведомление d (nolock)')
    mylog.info(unicode(q))
    cur = q()
    print cur.fetchall()
    for item in cur:
        mylog.info(item)
    q2 = db.query(u'select $Перечисление.СтатусыЗаказа.Задержка')
    mylog.info(unicode(q2))
    mylog.info(unicode( db.query(u' $ОбщийРеквизит.Фирма,  $ОбщийРеквизит.ДатаСозданияДокумента, $Журнал.ДатаДок, $Журнал') ))
    #print unicode(metadata)

if __name__ == '__main__':
    logging.getLogger('v7.prepare').setLevel(logging.DEBUG)
    logging.getLogger('v7.metadata').setLevel(logging.DEBUG)
    test()
