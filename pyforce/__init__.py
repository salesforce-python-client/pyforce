from __future__ import absolute_import
from __future__ import unicode_literals

import logging

from pyforce.pyclient import Client as PythonClient
from pyforce.xmlclient import Client as XMLClient
from pyforce.xmlclient import SessionTimeoutError
from pyforce.xmlclient import SoapFaultError

__all__ = (
    'PythonClient',
    'SoapFaultError',
    'SessionTimeoutError',
    'XMLClient'
)


class NullHandler(logging.Handler):
    def emit(self, record):
        pass


logging.getLogger("pyforce").addHandler(NullHandler())
