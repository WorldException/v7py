#!/usr/bin/env python
#-*-coding:utf8-*-
import logging
mylog = logging.getLogger('v7.work')
logging.getLogger('v7.reader').setLevel(logging.WARNING)
logging.getLogger('v7.prepare').setLevel(logging.INFO)
logging.getLogger('v7.metadata').setLevel(logging.INFO)

from v7.config import BaseConfig
from v7.base import Base

class Work(BaseConfig):
    NAME = 'work'
    #PATH_META_LOCAL = os.path.join(BaseConfig.PATH_META_LOCAL, NAME)
    PATH_TO_BASE = '/work'
    PATH_TYPE = 'smb' # smb|dir|ftp

    SMB_SERVER = '192.168.1.28'
    SMB_SHARE  = 'v7'
    SMB_USER = 'v7'
    SMB_PWD = 'V&123456'

class WorkDev(Work):
    NAME = 'workdev'
    PATH_TO_BASE = '/workdev'

db = Base(Work)

# выборка текущих статусов для обновления в емекс

query_statuses = u"""
    select
        d.НаСайт НаСайт,
        ж.НомерДок НомерДок,
        ж.ДатаДок ДатаДок,
        case t.#Статус $Перечисление.СтатусыЗаказа.case Статус,
        h.Наименование Характеристика,
        t.#КоличествоВБазе ВБазе,
        t.#КоличествоНаСайте НаСайте,
        t.#ОжидаемаяДата Ожидаем
    from $Документ.Уведомление d (nolock)
        join $Документ.#Уведомление t (nolock) on d.Код=t.iddoc
        join $Справочник.ХарактеристикиНоменклатуры h (nolock) on t.#ХарактеристикаТовара = h.id
        join $Журнал ж (nolock) on ж.IDDOC = d.Код
    where ж.ДатаДок between %(start)s and %(end)s
        and ж.ВидДокумента = d.ВидДокумента
        and h.Наименование like 'L%%'
"""

query_status_ref_local = u"""
    select
        d.НаСайт НаСайт,
        ж.НомерДок НомерДок,
        ж.ДатаДок ДатаДок,
        case t.#Статус $Перечисление.СтатусыЗаказа.case Статус,
        h.Наименование Характеристика,
        t.#КоличествоВБазе ВБазе,
        t.#КоличествоНаСайте НаСайте,
        t.#ОжидаемаяДата Ожидаем
    from $Документ.Уведомление d (nolock)
        join $Документ.#Уведомление t (nolock) on d.Код=t.iddoc
        join $Справочник.ХарактеристикиНоменклатуры h (nolock) on t.#ХарактеристикаТовара = h.id
        join $Журнал ж (nolock) on ж.IDDOC = d.Код
    where ж.ДатаДок between %(start)s and %(end)s
        and ж.ВидДокумента = d.ВидДокумента
        and h.Наименование = '%(ref)s'
    order by
        ж.ДатаДок desc
"""