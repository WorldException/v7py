#-*-coding:utf8-*-
import logging, os
logging.basicConfig()
mylog = logging.getLogger('v7')
mylog.setLevel(logging.INFO)

#logging.getLogger('v7.prepare').setLevel(logging.DEBUG)
#logging.getLogger('v7.metadata').setLevel(logging.DEBUG)

def getDataPath(filename):
    return os.path.join(os.path.dirname(__file__), 'data', filename)
LocalPath = os.path.dirname(__file__)
LocalPathData = os.path.join(os.path.dirname(__file__), 'data')
LocalMdPath = getDataPath('1Cv7.MD')


from .dds_parser import parse as parse_dds
from .md_reader import parse_md, extract_metadata
#from core import Application
from .db import MS_Proxy
