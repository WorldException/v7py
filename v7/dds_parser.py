#-*-coding:utf8-*-
'''
Evgeniy Stoyanov quick.es@gmail.com
1cv7 metadata parser ans sql helper

todo: http://habrahabr.ru/post/239081/

'''
import os

meta = {}
by_name={}
by_sql={}

True_='1'
False_='0'

import pprint
class MyPrettyPrinter(pprint.PrettyPrinter):
    def format(self, object, context, maxlevels, level):
        if isinstance(object, unicode):
            return (object.encode('utf8'), True, False)
        return pprint.PrettyPrinter.format(self, object, context, maxlevels, level)
myprint = MyPrettyPrinter(indent=2,width=200)

div_class="exp"

class DDS_Field(dict):
    u'''
    Максимальная длина названия поля, учесть при сравнении
    ГоловнаяОрганизац
    '''
    REPLACES = {
        'ID object': 'Id',
        'Object is Marked for': u'Помечен',
        'Row ID': u'НомерСтроки',
        'LineNo': u'НомерСтроки',
        'Version stamp': u'Время',
        'object code': u'Код',
        'object description': u'Наименование',
        'Parent in other tabl': 'Parentext',
        'ID parent obj': u'Родитель',
        'Is Line - Folder': u"ЭтоПапка",
        "ID Document's": u"Код"
    }
    def __init__(self,dds_obj):
        # Name                  |Descr               |Type|Length|Precision
        #F=ROW_ID                |Row ID              |I   |0     |0
        self.fieldstr = [d.strip() for d in dds_obj._curline_().split('|')]
        self['sql']=self.name
    @property
    def name(self):
        return self.fieldstr[0][2:]
    @property
    def sql(self):
        return self['sql']
    @property
    def desc(self):
        dsc = self.fieldstr[1]
        if DDS_Field.REPLACES.has_key(dsc):
            return DDS_Field.REPLACES[dsc]
        return self.fieldstr[1].replace(u'(P)','')
    @property
    def type(self):
        return self.fieldstr[2].strip()
    def as_div(self):
        return u'<div class="%s">%s, %s</div>' % (div_class, self.name, self.sql)

    #def __cmp__(self, other):
    #    if

class DDS_Table(dict):
    def __init__(self, dds_obj):
        self.dds_obj = dds_obj
        #==TABLE no 36     : Справочник мегапрайсСоответствияПроизводителейлей
        self.tablehead = dds_obj._curline_().split(':')[1].strip()#.replace(u' (Дв.)', u'Движения')

        self._name_type = self.tablehead.split(" ")[0]
        self._desc_ = self.tablehead #tablestr[1]
        parts = self.tablehead.split(' ')
        if len(parts)==2:
            self._desc_ = parts[1]
        elif len(parts)==3:
            self._desc_ = u"%sСтроки" % parts[2]

        dds_obj._nextline_()
        dds_obj._nextline_()
        #T=SC3956  |Справочник мегапрайсСоответств|SC3956     |R
        self.tablestr=[d.strip() for d in dds_obj._curline_().split('|')]
        self['sql'] = self.tablestr[0][2:]
        dds_obj._nextline_()
        dds_obj._nextline_()
        while dds_obj._nextline_():
            if dds_obj._curline_()[:2] == "F=":
                field = DDS_Field(dds_obj)
                field_name = field.desc
                i = 1
                while self.has_key(field_name):
                    # т.к. в dds длина наименования ограничивается, то некоторые имена попадаются обрезанными
                    # поэтому нумерую их
                    field_name = u"%s%s" % (field.desc, i)
                    i+=1
                self[field_name] = field
            else:
                break

    @property
    def name_type(self):
        return self._name_type
        #return self.tablehead.split(" ")[0]
    @property
    def sql(self):
        return self['sql']
    @property
    def desc(self):
        return self._desc_
        '''
        parts = self.tablehead.split(' ')
        if len(parts)==2:
            return parts[1]
        elif len(parts)==3:
            return u"%sСтроки" % parts[2]
        return self.tablehead #tablestr[1]
        '''
    @property
    def name(self):
        return self.desc
    def as_div(self):
        r = u'<div class="%s">%s ' % (div_class, self.name)
        r += "".join([fobj.as_div() for fobj in self.values()]) + u'</div>'
        return r

# def getLocal(filename):
#     ''' получить полное имя файла относительно скрипта '''
#    return u"%s%s%s" % (os.path.dirname(os.path.abspath(__file__)), os.sep, filename)

class DDS(dict):
    ''' структура метаданных '''
    BOOKS = u"Справочник"
    def __init__(self, ddsfilename):
        self.line = ''
        self.filename = ddsfilename
        self[DDS.BOOKS]={}
        self[u"Документ"]={}
        self[u"Регистр"]={}
        self.parse()
        self.name = 'config'
    def _nextline_(self):
        line= self.filedds.readline()
        self.line = line.decode('cp1251')
        return len(self.line)>0
    def _curline_(self):
        return self.line
    def parse(self):
        self.filedds = open(self.filename,'r')
        while self._nextline_():
            line = self._curline_()
            if line.startswith("#==TABLE"):
                table = DDS_Table(self)
                #print u"new table: %s.%s" % (table.name_type, table.desc)
                if self.has_key(table.name_type):
                    self[table.name_type][table.desc] = table
        self.filedds.close()
    def prepareSQL(self, sqltext, debug=False):
        '''
        найти заготовки вида <name> <Справочник.Контрагенты> <Справочник Контрагенты.Наименование>
        '''
        import re
        errors = False
        sqlres = u"%s" % sqltext
        for m in re.finditer(ur'\{([a-zа-я0-9\.^ ]+)\}|\$([a-zа-я0-9\.^ ]+)', sqltext, re.UNICODE|re.IGNORECASE):
            #print 'group(0)',m.group(0),m.group(2)
            obj = m.group(1)
            if not obj:
                obj = m.group(2).strip()
            #print "group(1):",obj
            parts = obj.split(".")
            sql = m.group(1)
            meta = self
            if meta.has_key(parts[0]):
                meta = meta[parts[0]]
            for part in parts[1:]:
                if meta.has_key(part):
                    #myprint.pprint(meta[part])
                    sql = meta[part].sql
                    meta = meta[part]
                else:
                    sql = u"<!not found [%s] in %s>" % (part, obj)
                    errors = True
                    break
            if debug:
                print m.group(0),"->", sql
            sqlres = sqlres.replace(m.group(0), sql)
        if errors:
            raise RuntimeError(u"errors prepare sql:%s" % sqlres)
        return sqlres
    def pprint(self):
        myprint.pprint(self)

    def as_div(self):
        r = u'<div class="%s">%s</div>' % div_class
        tr = []
        for tgroup,tbls in self.items():
            t = '<div>%s</div>' % tgroup
            #for tbl in t

        return r
# пытаюсь загрузить файл описания в папке со скриптом
from v7 import getDataPath
dds_filename = getDataPath('1Cv7.DDS')
dds = None
class DdsFileNotFoundException(RuntimeError): pass
def read_dds():
    global dds
    if dds is None:
        if os.path.exists(dds_filename):
            dds = DDS(dds_filename)
    if dds is None:
        raise DdsFileNotFoundException(dds_filename)

def parse(query, debug=False):
    '''
     собственно говоря преобразует запрос к нужному виду
    '''
    read_dds()
    if debug:
        print "source query"
        print query
        result = dds.prepareSQL(query, True)
        print "result"
        print result
        return result
    else:
        return dds.prepareSQL(query)
