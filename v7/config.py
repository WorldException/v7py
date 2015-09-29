#!/usr/bin/env python
#-*-coding:utf8-*-
import logging
log = logging.getLogger(__name__)

import os
def getpath(filename=''):
    return os.path.join(os.path.dirname(__file__), filename)

class BaseConfig:
    NAME = 'default'
    PATH_TYPE = 'dir' # smb|dir|ftp

    SMB_SERVER = ''
    SMB_SHARE  = ''
    SMB_USER = ''
    SMB_PWD = ''

    # общий путь к папке с метаданными
    PATH_META = getpath('meta')
    # полный путь к папке метаданных 1С с учетом имени (для этой базы)
    PATH_META_DIR = ''
    # полный путь к моделям на py
    PATH_TO_MODEL = ''

    FILE_1Cv7_MD = u'1Cv7.MD'
    FILE_1Cv7_DDS = u'1Cv7.DDS'
    FILE_1Cv7_DBA = u'1Cv7.DBA'
    FILES = (FILE_1Cv7_MD, FILE_1Cv7_DDS, FILE_1Cv7_DBA)
    # абсолютные пути к файлам после инициализации
    PATH_1Cv7_MD = ''
    PATH_1Cv7_DDS = ''
    PATH_1Cv7_DBA = ''

    def __init__(self):
        self.init_config()

    @classmethod
    def METAFILE_FULL_PATH(cls, filename):
        return os.path.join(cls.PATH_META_DIR, filename)

    @classmethod
    def init_config(cls):
        cls.PATH_META_DIR = os.path.join(cls.PATH_META, cls.NAME)
        cls.PATH_TO_MODEL = os.path.join(cls.PATH_META_DIR, 'model')
        cls.PATH_1Cv7_DBA = cls.METAFILE_FULL_PATH(cls.FILE_1Cv7_DBA)
        cls.PATH_1Cv7_DDS = cls.METAFILE_FULL_PATH(cls.FILE_1Cv7_DDS)
        cls.PATH_1Cv7_MD = cls.METAFILE_FULL_PATH(cls.FILE_1Cv7_MD)
        for dirpath in (cls.PATH_META_DIR, cls.PATH_TO_MODEL):
            if not os.path.exists(dirpath):
                log.info(u'Create dir for %s=%s' % (cls.__name__, dirpath))
                os.makedirs(dirpath)

    @classmethod
    def update_meta_files(cls):
        log.info(u'Start update meta files: %s' % cls.__unicode__())
        if cls.PATH_TYPE == 'smb':
            import smbclient
            smb = smbclient.SambaClient(cls.SMB_SERVER, cls.SMB_SHARE, cls.SMB_USER, cls.SMB_PWD)
            #print smb.listdir('/')
            workdir = smb.listdir(cls.PATH_TO_BASE)
            log.debug(u'Files on smb: %s' % repr(workdir))
            for filename in cls.FILES:
                if filename in workdir:
                    fullname = os.path.join(cls.PATH_TO_BASE, filename)
                    target_name = cls.METAFILE_FULL_PATH(filename)
                    log.info(u'downloading: %s -> %s' % (fullname, target_name))
                    smb.download(fullname, target_name)
            return True

        if cls.PATH_TYPE == 'dir':
            workdir = os.listdir(cls.PATH_TO_BASE)
            log.debug(u'Files on smb: %s' % repr(workdir))
            for filename in cls.FILES:
                if filename in workdir:
                    fullname = os.path.join(cls.PATH_TO_BASE, filename)
                    target_name = cls.METAFILE_FULL_PATH(filename)
                    log.info(u'copying: %s -> %s' % (fullname, target_name))
                    fsrc = open(fullname, 'rb', 1024)
                    try:
                        fout = open(target_name, 'wb', 1024)
                        fout.write(fsrc.read())
                    finally:
                        fsrc.close()
                        fout.close()
            return True

    @classmethod
    def __unicode__(cls):
        return u"1Cv7 config[%s]: %s path: %s type: %s" % (cls.__name__, cls.NAME, cls.PATH_TO_BASE, cls.PATH_TYPE)
