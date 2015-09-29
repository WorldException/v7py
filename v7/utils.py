#!/usr/bin/env python
# -*-coding:utf8-*-
import re
re_unicode = re.compile(r'\\u[0-9a-f]{4}')
def fixunicode(str1, encoding=''):
    '''
    :param str1: convert "\u041a\u043e\u043c\u0430\u043d" to unicode
    :return: unicode
    '''
    s = re_unicode.findall(str1)
    s = list(set(s))

    r = str1
    for i in s:
        r = r.replace(i, eval('u"\u%s"' % i[2:]))
    if encoding:
        r = r.decode(encoding)
    return r

import repr as reprlib

class MyRepr(reprlib.Repr):
    def __init__(self):
        reprlib.Repr.__init__(self)
        self.maxstring = 1000
        self.maxlong = 1000
        self.maxlist = 50
        self.maxarray = 50
        self.maxdict = 50
        self.maxlevel=20
    def repr_unicode(self, obj, level):
        #print 'unicode:',obj
        return obj
    def repr_str(self, obj, level):
        #print 'str:',obj
        return obj
    def repr_list(self, obj, level):
        otstup = u' '*level
        rstr = u'\n'+otstup+u'['
        for i in obj:
            rstr += repr(i)
            rstr += u',\n'
            rstr += otstup
        rstr = rstr[:-(level+1)] + u']\n'
        return rstr

    def repr(self,data):
        rstr = reprlib.Repr.repr(self,data)
        return rstr

mrepr = MyRepr()


# конвертация между системами счисления
def baseN(num,b,numerals="0123456789abcdefghijklmnopqrstuvwxyz"):
    return ((num == 0) and numerals[0]) or (baseN(num // b, b, numerals).lstrip(numerals[0]) + numerals[num % b])

def convert_n_to_m(x,n,m):
    if n<1: return False
    if m<1 or m>36: return False
    if type(x)==type(0):
        #numeric
        if m==1:
            d='%d'%x
            try:
                d=int(d,n)
                return '0'*d
            except:
                return False
        else:
            return baseN(x,n).upper()
    elif type(x)==type(''):
        #string
        if m==1:
            try:
                d=int(x,n)
                return '0'*d
            except:
                return False
        else:
            try:
                q=int(x,n)
                return baseN(q,m).upper()
            except:
                return False
    else:
        return False

def convert_n_to_m2(x, n, m):
    available_symbols = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if (((type(x) != str) and (type(x) != int)) or (n < 1) or (n > 36) or (m < 1) or (m > 36)):
        return False
    else:
        if (type(x) == int):
            x = str(x)
        allowed_symbols = available_symbols[0 : n]
        if (False in map(lambda symbol: True if (symbol in allowed_symbols) else False, x)):
            return False
        else:
            value = len(x) if (n == 1) else int(x, n)
            result = ""
            if (m > 1):
                while (value > 0):
                    result += str(available_symbols[value % m])
                    value /=  m
            else:
                result = '0' * value
            return result[ : : -1]

def ID_36(value_10):
    return '{:^9}'.format(convert_n_to_m2(value_10, 10, 36))