#!/usr/bin/env python
# -*-coding:utf8-*-
from v7 import mylog

def read_dba(filename, dict_ret=False):
    buff = ''
    with open(filename, 'rb') as f:
        buff = f.read()
    mylog.debug('buff [%s]' % buff)
    key = "19465912879oiuxc ensdfaiuo3i73798kjl".encode("US-ASCII")
    mylog.debug(key)
    ##decode[i] = ((byte)(buf[i] ^ SQLKeyCode[(i % 36)]));
    decode = []
    s = ''
    for i in xrange(0, len(buff)):
        b = ord(buff[i]) ^ ord(key[(i%36)])
        decode.append( b )
        s += chr(b)
    mylog.debug(s)
    s = s.replace('","','":"').replace('{{','{').replace('}}','}').replace('},{',',')
    #mylog.debug(s)
    v = eval(s)
    #mylog.debug(repr(v))
    if dict_ret:
        return v
    Server, DB, Login, Password = v["Server"], v["DB"], v["UID"], v["PWD"]
    mylog.debug(repr([Server, DB, Login, Password]))
    return Server, DB, Login, Password
    #{{"Server","192.168.1.30"},{"DB","work"},{"UID","sa"},{"PWD","xxxeral!"},{"Checksum","bf062f4f"}}


if __name__ == '__main__':
    from v7 import getDataPath
    server, db, user, pwd = read_dba(getDataPath('1Cv7.DBA'))
    mylog.debug("Server: %s" % server)