#!/usr/bin/env python
#-*-coding:utf8-*-

import smbclient

smb = smbclient.SambaClient('192.168.1.28', 'v7', 'v7', 'V&123456')
print smb.listdir('/')
work = smb.listdir('/workdev')
print work
if u'1Cv7.DDS' in work:
    print 'download', smb.download('/workdev/1Cv7.DDS', '/tmp/1Cv7.DDS')

