import logging
from xmlclient import _tPartnerNS, _tSObjectNS, _tSoapNS, SoapFaultError, SessionTimeoutError, DEFAULT_SERVER_URL
from xmlclient import Client as XMLClient
from pyforce import Client as PythonClient

__all__ = ('XMLClient', '_tPartnerNS', '_tSObjectNS', '_tSoapNS', 'tests',
        'SoapFaultError', 'SessionTimeoutError', 'PythonClient', 'DEFAULT_SERVER_URL')

class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger("pyforce").addHandler(NullHandler())
