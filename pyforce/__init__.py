'''pyforce is there to access the RESTful Force.com API'''

import logging

from pyforce.xmlclient import (
    _tPartnerNS,
    _tSObjectNS,
    _tSoapNS,
    DEFAULT_SERVER_URL,
    SoapFaultError,
    SessionTimeoutError
)
from pyforce.xmlclient import Client as XMLClient
from pyforce.pyforce import Client as PythonClient

__all__ = (
    'XMLClient',
    '_tPartnerNS',
    '_tSObjectNS',
    '_tSoapNS',
    'DEFAULT_SERVER_URL',
    'PythonClient',
    'SoapFaultError',
    'SessionTimeoutError'
)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass

logging.getLogger("pyforce").addHandler(NullHandler())
