#!/usr/bin/env python
# -*-coding:utf8-*-
import logging
mylog = logging.getLogger('v7.prepare')

import re

class PrepareError:
    pass

def prepareSQL(sql, md, debug=False):
    '''
    найти заготовки вида <name> <Справочник.Контрагенты> <Справочник Контрагенты.Наименование>
    '''
    mylog.debug(u"src sql: %s" % sql)
    errors = False
    sqlres = u"%s" % sql
    psevdo = {} # псевдонимы таблиц
    for m in re.finditer(ur'(\$[#a-zа-я0-9\.^]+)\s+as\s+([a-zA-Z_0-9а-я]+)'
                         ur'|(\$[#a-zа-я0-9\.^]+)\s+([a-zA-Z_0-9а-я]+)'
                         ur'|(\$[#a-zа-я0-9\.^]+)',
                         sql, re.UNICODE|re.IGNORECASE|re.MULTILINE):
        #print 'group(0)',m.group(0),m.group(2)
        #print m.groups()
        ps = ''
        obj = ''
        if m.group(1):
            obj = m.group(1)
            ps = m.group(2)
        elif m.group(3):
            obj = m.group(3)
            ps = m.group(4)
        elif m.group(5):
            obj = m.group(5)
        if not obj:
            raise PrepareError('error parser groups')
        search_str = obj[1:].strip()
        field = md.get_by_path(search_str)
        sql = field.sql
        mylog.debug(u"Алиас: %s -> %s, псевдоним %s" % (m.group(0), sql, ps))
        if ps:
            psevdo[ps] = (m.group(0), obj, sql, field) # запоминаю замену для псевдонима
        sqlres = sqlres.replace(obj, sql)
    # а теперь вычислю значения для псевдонимов
    #print 'aliases:', psevdo
    for p_alias, ps in psevdo.items():
        # ur'[$\n\s\t,]%s.([#a-zA-Z0-9А-Яа-я_]+)]'
        reg = ur'([$\n\s\t,]%s)\.([#a-zA-Z0-9А-Яа-я_]+)' % p_alias
        for m in re.finditer(reg, sqlres, re.UNICODE|re.IGNORECASE):
            pre = m.group(0)[0] # символ перед псевдонимом
            fld = ps[3].get_by_path([m.group(2),])
            mylog.debug(u"Псевдоним: %s.%s -> %s" % (p_alias, m.group(2), fld.sql))
            if fld.sql[0] == '!':
                #замена всего выражения
                sqlres = sqlres.replace(m.group(0), u"%s%s" % (pre, fld.sql[1:]))
            else:
                sqlres = sqlres.replace(m.group(0), u"%s.%s" % (m.group(1), fld.sql))
    if errors:
        raise RuntimeError(u"errors prepare sql:%s" % sqlres)
    mylog.debug(u"RETURN: %s" % sqlres)
    return sqlres