
import logging

from pyforce.xmlclient import (
    Client as XMLClient, SoapFaultError, SessionTimeoutError)
from pyforce.pyclient import Client as PythonClient

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
