#!/usr/bin/env python
# -*-coding:utf8-*-
# полезное по прямым запросам
# http://www.1cpp.ru/forum/YaBB.pl?num=1148038411
# описание таблиц
# http://www.script-coding.com/v77tables.html
import logging
mylog = logging.getLogger('v7.metadata')
from v7 import utils

# Тип данных
FT_TEXT  = 'C'
FT_FLOAT = 'N'
FT_INT   = 'I'
FT_DATA  = 'D'

# тип поля
FC_ATTR  = 'A'  # атрибут
FC_HEAD  = 'H'  # реквизит шапки
FC_TABLE = 'T'  # реквизит табличного поля
FC_DT    = 'DT' # табличное поле

# маски для формирования SQL представлений согласно типу поля
field_sql_mask = {
    FC_ATTR:  u'%s',
    FC_HEAD:  u'SP%s',
    FC_TABLE: u'SP%s',
    FC_DT:    u"DT%s"
}

def oprint(obj):
    r= u"ATTR:\nname:%s\nsql:%s\ndescr:%s\n" % (obj.name, obj.sql, '')
    # for key, value in obj.items():
    #     r += "%s = %s\n" % (key, value)
    #     #print type(value), value
    r += u'FIELDS:\n'
    for f in obj.fields:
        r += u"%s\n" % f
    return r


class FieldNotFound(RuntimeError):
    pass


class MetaObject(dict):
    '''
    Базовый класс для всех остальных обьектов метаданных
    parser - структура определяющая какому атрибуту какое поле присвоить из входящей структуры из MD
    meta - это соотвествия для корневого списка
    пример структуры
    [2901, 'ИмяОбъекта', "", "Описание или синоним, ['Fields', [342, 'Реквизит', ...],..]
    '''
    ru_name = u"Документ"
    md_name = "Documents"
    parser = {
        'meta': {
            '_sql':0, # поле _sql по индексу 0
            '_name': 1,
            '_description': 3,
        }
    }

    field_prefix = ''
    table_prefix = ''

    print_metadata = False

    # спец. тип вроде журнала, констант и т.д. имеющий одно представление (одну таблицу)
    special = False

    def __init__(self, name=''):
        self._sql = ''
        self._name = name
        self._description = ''
        # список полей в базе данных, как шапки так и табличных
        self.fields = []
        self.need_table = False
        self.parent = None
        self.md = None

    def __find_field__(self, name, place=[FC_HEAD, FC_ATTR]):
        '''
        Поиск реквизита по наименованию и типу
        :param name: имя реквизита как есть
        :param place: тип поля
        :return: обьект поля
        '''
        if name.startswith("#"):
            place = FC_TABLE
            name = name[1:]
        _name = name.lower()
        for f in self.fields:
            if place and type(f) is FieldObject and f._place not in place:
                continue
            if f.name.lower() == _name:
                return f
        raise FieldNotFound(_name.encode('utf8'))

    def addField(self,f):
        f.parent = self
        self.fields.append(f)

    def getFields(self):
        #ToDo: если это ссылка на другой элемент метаданных то вернуть его поля
        return self.fields

    @property
    def sql(self):
        '''
        :return: возращает текстовое представление в бд
        '''
        pref = u""
        if (not self.parent is None) and len(self.parent.dbo_name)>0:
            pref = u"%s." % self.parent.dbo_name
        if self.need_table:
            return u"%s%s%s" % (pref, self.table_prefix, self._sql)
        else:
            return u"%s%s%s" % (pref, self.field_prefix, self._sql)

    @property
    def name(self):
        return self._name

    def __unicode__(self):
        return u'Obj:(%s)[%s]\n%s' % (self.ru_name, self.md_name, oprint(self))

    def __str__(self):
        return self.__unicode__()

    def get_by_path(self, path):
        '''
        Получить рекурсивно объект по пути
        :param path: [документ,поступление,датадок]
        :return: найденый обьект
        '''
        if len(path)==0:
            return self
        # if type(path) in (str, basestring, unicode):
        #     path = path.lower().split('.')
        key = path.pop()
        #print 'key:',key
        return self.__find_field__(key).get_by_path(path)

    def after_parse(self):
        # действия по завершению создания парсингом, для перекрытия в наследниках
        pass

    @classmethod
    def print_metadata_info(cls, m, level=0):
        if cls.print_metadata:
            if level==0:
                mylog.info(u"Metadata %s, %s" % (cls.ru_name, cls.md_name))
            for i in m:
                mylog.info(u'>%s%s' % ('>'*level, i))
                if type(i)==list:
                    cls.print_metadata_info(i, level+1)

    @classmethod
    def parse(cls, m):
        '''
        Выполняет разбор структуры md файла в набор обьектов
        Каждый класс может по своему парсить свой набор,но это подходит для многих
        :param m:
        :return:
        '''
        cls.print_metadata_info(m)
        # сначала беру основные атрибуты
        doc = cls()
        for attr_name, index in cls.parser['meta'].items():
            #doc.__setattr__(attr_name, m[index])
            setattr(doc, attr_name, m[index])
        # теперь разбираю информацию о полях
        for i in m:
            # для вложенных полей ищу сопадающие правила
            if type(i) == list:
                if cls.parser.has_key(i[0]):
                    fieldparser = cls.parser[i[0]]
                    for h in i[1:]:
                        f = fieldparser(h)
                        f.parent = doc
                        doc.addField(f)
        doc.after_parse()
        return doc


class FieldObject(MetaObject):
    def __init__(self, name='', sql='', place=FC_HEAD):
        MetaObject.__init__(self)
        self._place = place
        self._name = name
        self._sql = sql

    def __unicode__(self):
        return u'Field[%s]:{%s, %s }' % (self._place, self.name, self.sql)

    @classmethod
    def parse(cls, m, parser, place=FC_HEAD):
        f = FieldObject(place=place)
        for attr_name, index in parser.items():
            setattr(f, attr_name, m[index])
        return f

    @property
    def sql(self):
        return field_sql_mask[self._place] % self._sql

# обработчики для создания парсеров поименно
def field_parser(rulles, place):
    #ToDo откуда берется m??!!
    def parser(m):
        return FieldObject.parse(m, rulles, place)
    return parser

def object_parser(cls):
    def parser(m):
        return cls.parse(m)
    return parser


class DocumentObject(MetaObject):
    ru_name = u"Документ"
    md_name = "Documents"
    parser = {
        'meta':{
            '_sql':0,
            '_name': 1,
            '_description': 3,
        },
        'Head Fields': field_parser({'_sql': 0, '_name':1}, FC_HEAD),
        'Table Fields':field_parser({'_sql': 0, '_name': 1}, FC_TABLE)
    }
    field_prefix = 'DH'
    table_prefix = 'DT'

    #print_metadata = True

    def __init__(self):
        MetaObject.__init__(self,'')

    def after_parse(self):
        # добавляю дополнительные поля
        self.addField(FieldObject(name=u"ТабличнаяЧасть", sql=self._sql, place=FC_ATTR))
        self.addField(FieldObject(name=u"Код", sql="iddoc", place=FC_ATTR))
        self.addField(FieldObject(name=u"НомерСтроки", sql="LINENO_", place=FC_ATTR))
        self.addField(FieldObject(name=u'ВидДокумента', sql='!%s' % self._sql, place=FC_ATTR))
        #self.addField(FieldObject(name=u"Код", sql="code", place=FC_ATTR))


class AllDocumentFieldObject(MetaObject):
    """
    Общие реквизиты документов
    могут хранитьв журнале и в таблице документов
    """
    ru_name = u"ОбщийРеквизит"
    md_name = "GenJrnlFldDef"
    #instance = None

    def __init__(self, name=''):
        MetaObject.__init__(self, name)
        #self._name = u'ОбщийРеквизит'

    parser = {
        'meta': {
            '_sql': 0,
            '_name': 1,
            '_description': 2,
            '_in_journ': 10 # 1 реквизит с отбором, значит в журнале, иначе в табл. документа
        },
    }
    #print_metadata = True

    @property
    def sql(self):
        if self._in_journ:
            return 'SP%s' % self._sql
        else:
            return '!!SeeDocumentTable!!'

    '''
    @classmethod
    def parse(cls, m):
        cls.print_metadata_info(m)
        if not cls.instance:
            cls.instance = cls()
        doc = cls.instance
        f = FieldObject.parse(m, cls.parser['meta'], FC_ATTR)
        f.parent = doc
        doc.addField(f)
        return doc
    '''

class CatalogObject(MetaObject):
    ru_name = u"Справочник"
    md_name = "SbCnts"
    parser = {
        'meta':{
            '_sql':0,
            '_name': 1,
            '_description': 2,
        },
        'Params': field_parser({
            '_sql': 0,
            '_name':1
        },FC_HEAD),
    }
    field_prefix = 'SC'
    table_prefix = 'SC'

    def __init__(self):
        MetaObject.__init__(self)

    def after_parse(self):
        self.addField(FieldObject(name=u"ID", sql="id", place=FC_ATTR))
        self.addField(FieldObject(name=u"Код", sql="code", place=FC_ATTR))
        self.addField(FieldObject(name=u"Наименование", sql="descr", place=FC_ATTR))
        self.addField(FieldObject(name=u"ПометкаНаУдаление", sql="ismark", place=FC_ATTR))
        self.addField(FieldObject(name=u"ЭтоГруппа", sql="isFolder", place=FC_ATTR))
        self.addField(FieldObject(name=u"Родитель", sql="parentid", place=FC_ATTR))


class RegisterObject(MetaObject):
    ru_name = u"Регистр"
    md_name = "Registers"
    parser = {
        'meta': MetaObject.parser['meta'],
        'Props': field_parser({
            '_sql': 0,
            '_name': 1
        }, FC_HEAD),
        'Figures': field_parser({
            '_sql': 0,
            '_name':1
        }, FC_HEAD),
        'Flds': field_parser({
            '_sql': 0,
            '_name':1
        }, FC_HEAD),
    }
    field_prefix = 'RG'
    table_prefix = 'RA'


class EnumObject(MetaObject):
    ru_name = u'Перечисление'
    md_name='EnumList'
    parser = {
        'meta': MetaObject.parser['meta'],
        'EnumVal': field_parser({'_sql': 0, '_name':1}, FC_ATTR),
    }

    def after_parse(self):
        # добавить спец поля для представления списком и т.д case 123 $перечисление.чегото.case Name
        sql_to_name_case = u''
        for item in self.fields:
            sql_to_name_case += u"\n when '%s' then '%s'" % (utils.ID_36(item._sql), item._name)
        sql_to_name_case += u"\nelse '' end\n"
        self.addField(FieldObject('case', sql_to_name_case, FC_ATTR))

    @property
    def sql(self):
        return u'%s %s' % (self._sql, self._name)


class JournObject(MetaObject):
    """
    создается вручную без парсера
    """
    ru_name = u'Журнал'
    special = True

    def __init__(self, name=''):
        MetaObject.__init__(self, name)
        self._name = u'Журнал'
        self._sql = '_1SJourn'

        self.addField(FieldObject('ROW_ID','ROW_ID',FC_ATTR))
        # [int] – идентификатор журнала, ID объекта класса Journalisters, значение в 36/64-ричной системе
        # (в зависимости от версии V7). Тип – Char(4). Определяется реквизитом Documents.Jrnl_ID.
        # Фактически 1SJourn – это «полный журнал».
        self.addField(FieldObject('IDJOURNAL','IDJOURNAL',FC_ATTR))
        # [int] – PKey документа, такой же как в DHxxx и DTxxx. Тип – Char(9). IDDOC всех документов хранятся в 1SJourn.
        self.addField(FieldObject('IdDoc','IDDOC',FC_ATTR))
        # [int] – ссылка на ID объекта-таблицы Documents.ID. Тип – Char(4).
        self.addField(FieldObject(u'ВидДокумента','IDDocDef',FC_ATTR))
        # возможность документа работать с компонентами: оперативный учет (1), расчет (2), бухучет (4) – и их комбинация.
        # Для документа «Операция» APPCODE=20. Тип – Numeric(3,0). Возможно, существуют и другие значения.
        # Возможность работы с различными компонентами определяется значениями Documents.PrTrade, Documents.PrSalary, Documents.PrAccount.
        self.addField(FieldObject('AppCode','APPCode',FC_ATTR))
        # дата документа. Тип – Date(8).
        self.addField(FieldObject(u'ДатаДок','DATE_TIME_IDDOC',FC_ATTR))
        self.addField(FieldObject(u'НомерДок','DocNo',FC_ATTR))
        #  флаг закрытия/проведения документа. Тип – Numeric(1,0).
        self.addField(FieldObject(u'Проведен','CLOSED',FC_ATTR))
        self.addField(FieldObject(u'ПометкаНаУдаление','ISMark',FC_ATTR))
        # счетчик действий (движения) для данного документа (один документ может вызывать несколько движений регистра).
        # Похоже, что связан с полями ACTNO таблиц RAxxx и 1SCONST. Тип – Numeric(6,0).
        self.addField(FieldObject(u'ACTCNT','ACTCNT',FC_ATTR))


class MDErrorNotFound(RuntimeError):
    pass


class MDObject(dict):
    '''
    корневой обьект метаданных, содержит всю информацию по метаданным
    '''
    parser = {
        'Documents': DocumentObject,
        'SbCnts': CatalogObject,
        'Registers': RegisterObject,
        AllDocumentFieldObject.md_name: AllDocumentFieldObject,
        EnumObject.md_name: EnumObject,
    }

    def __init__(self, **kwargs):
        self.name = ''
        # имя которое будет добавлено к таблицам work.dbo
        self.dbo_name = ''
        for key, value in kwargs:
            setattr(self, key, value)

        self.items = [] # это любое из метаданных
        self.aliases = {
            u'документ': DocumentObject,
            u'справочник': CatalogObject,
            u'регистр': RegisterObject,
            u'перечисление': EnumObject,
            AllDocumentFieldObject.ru_name.lower(): AllDocumentFieldObject,
            JournObject.ru_name.lower(): JournObject
        }

        self.sql_to_field_index = {}

    def __update_sql_to_field_index__(self):
        ''' обновляет индекс соответствия имени поля в базе данных и обьект Поле'''
        self.sql_to_field_index.clear()
        for item in self.items:
            self.sql_to_field_index[item.sql] = item
            for field in item.fields:
                self.sql_to_field_index[field.sql] = field

    def getFieldNameBySQL(self, sqlname):
        name = sqlname.upper()
        if self.sql_to_field_index.has_key(name):
            return self.sql_to_field_index[name].name
        return sqlname

    def __find_by_name__(self, obj_list, name):
        # найти в списке элементов нужный вид
        name_ = name.lower()
        mylog.debug(u'__find_by_name__(%s)' % name_)
        for item in obj_list:
            if item.special:
                return item.get_by_path([name_,])
            if item.name.lower() == name_:
                return item
        raise MDErrorNotFound(name_) #encode('utf8')

    def _get_by_alias_(self, alias):
        # создает итератор по алиасу
        al = alias.lower()
        found = False
        mylog.debug(u'get_by_alias(%s)' % al)
        if self.aliases.has_key(al):
            cls = self.aliases[al]
            for item in self.items:
                if type(item) is cls:
                    found = True
                    #mylog.debug(u'found %s' % unicode(item))
                    yield item
        if not found:
            raise MDErrorNotFound(al.encode('utf8'))

    def get_by_path(self, path):
        '''
        Получить обьект по имени Справочник.Автомобили.Модель
        :param path:
        :return:
        '''
        # сначала по типу объекта ищу список доступных классов, походящих под тип
        if type(path) in (str, basestring, unicode):
            path = path.lower().split('.')
        if len(path) == 0:
            return None
        path.reverse()
        #mylog.info(u'%s' % repr(path))
        alias = path.pop()
        # сейчас путь может начинаться только с двух слов
        obj = self._get_by_alias_(alias)

        if len(path)==0:
            # возращаю только спец объекты
            for o in obj:
                if o.special:
                    return o

        name = path.pop()

        # теперь ищу нужный вид заданного типа == значению после .
        mylog.debug(u'Поиск второй части %s' % name.replace('#',''))
        o = self.__find_by_name__(obj, name.replace('#',''))
        o.need_table = True if name.startswith("#") else False

        return o.get_by_path(path)

    def x(self, path):
        return self.get_by_path(path)

    def parse(self, dds):
        parsers = self.parser.keys()
        for m in dds:
            typeGr = m[0]
            if typeGr=='TaskItem':
                self.name = m[1]
            elif typeGr in parsers:
                 cls = self.parser[typeGr]
                 for item in m[1:]:
                     obj = cls.parse(item)
                     obj.parent = self
                     self.items.append(obj)
            else:
                mylog.info(u'Нет парсера для %s' % typeGr)
        self.items.append(JournObject())
        self.__update_sql_to_field_index__()

    def __unicode__(self):
        s = []
        for item in self.items:
            s.append(unicode(item))
        return u'\n'.join(s)