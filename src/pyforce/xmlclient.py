__version__ = '1.1dev'
__author__ = "Simon Fell et al. reluctantly forked by idbentley"
__credits__ = "Mad shouts to the sforce possie"
__copyright__ = "GNU GPL 2."

import httplib
import logging
import socket
from urlparse import urlparse
from StringIO import StringIO
import gzip
import datetime
import xmltramp
from xmltramp import islst
from xml.sax.saxutils import XMLGenerator
from xml.sax.saxutils import quoteattr
from xml.sax.xmlreader import AttributesNSImpl

# global constants for namespace strings, used during serialization
_partnerNs = "urn:partner.soap.sforce.com"
_sobjectNs = "urn:sobject.partner.soap.sforce.com"
_envNs = "http://schemas.xmlsoap.org/soap/envelope/"
_noAttrs = AttributesNSImpl({}, {})

DEFAULT_SERVER_URL = 'https://login.salesforce.com/services/Soap/u/20.0'

# global constants for xmltramp namespaces, used to access response data
_tPartnerNS = xmltramp.Namespace(_partnerNs)
_tSObjectNS = xmltramp.Namespace(_sobjectNs)
_tSoapNS = xmltramp.Namespace(_envNs)

# global config
gzipRequest=True    # are we going to gzip the request ?
gzipResponse=True   # are we going to tell teh server to gzip the response ?
forceHttp=False     # force all connections to be HTTP, for debugging

_logger = logging.getLogger('pyforce.{0}'.format(__name__))

def makeConnection(scheme, host):
    if forceHttp or scheme.upper() == 'HTTP':
        return httplib.HTTPConnection(host)
    return httplib.HTTPSConnection(host)


# the main sforce client proxy class
class Client:
    def __init__(self, serverUrl=None):
        self.batchSize = 500
        self.serverUrl = serverUrl or DEFAULT_SERVER_URL
        self.__conn = None

    def __del__(self):
        if callable(getattr(self.__conn, 'close', None)):
            self.__conn.close()

    # login, the serverUrl and sessionId are automatically handled, returns the loginResult structure
    def login(self, username, password):
        lr = LoginRequest(self.serverUrl, username, password).post()
        self.useSession(str(lr[_tPartnerNS.sessionId]), str(lr[_tPartnerNS.serverUrl]))
        return lr

    # initialize from an existing sessionId & serverUrl, useful if we're being launched via a custom link
    def useSession(self, sessionId, serverUrl):
        self.sessionId = sessionId
        self.__serverUrl = serverUrl
        (scheme, host, path, params, query, frag) = urlparse(self.__serverUrl)
        self.__conn = makeConnection(scheme, host)

    # set the batchSize property on the Client instance to change the batchsize for query/queryMore
    def query(self, soql):
        return QueryRequest(self.__serverUrl, self.sessionId, self.batchSize, soql).post(self.__conn)

    def queryMore(self, queryLocator):
        return QueryMoreRequest(self.__serverUrl, self.sessionId, self.batchSize, queryLocator).post(self.__conn)

    def search(self, sosl):
        return SearchRequest(self.__serverUrl, self.sessionId, self.batchSize, sosl).post(self.__conn)

    def getUpdated(self, sObjectType, start, end):
        return GetUpdatedRequest(self.__serverUrl, self.sessionId, sObjectType, start, end).post(self.__conn)

    def getDeleted(self, sObjectType, start, end):
        return GetDeletedRequest(self.__serverUrl, self.sessionId, sObjectType, start, end).post(self.__conn)

    def retrieve(self, fields, sObjectType, ids):
        return RetrieveRequest(self.__serverUrl, self.sessionId, fields, sObjectType, ids).post(self.__conn)

    # sObjects can be 1 or a list, returns a single save result or a list
    def create(self, sObjects):
        return CreateRequest(self.__serverUrl, self.sessionId, sObjects).post(self.__conn)

    # sObjects can be 1 or a list, returns a single save result or a list
    def update(self, sObjects):
        return UpdateRequest(self.__serverUrl, self.sessionId, sObjects).post(self.__conn)

    # sObjects can be 1 or a list, returns a single upsert result or a list
    def upsert(self, externalIdName, sObjects):
        return UpsertRequest(self.__serverUrl, self.sessionId, externalIdName, sObjects).post(self.__conn)

    # ids can be 1 or a list, returns a single delete result or a list
    def delete(self, ids):
        return DeleteRequest(self.__serverUrl, self.sessionId, ids).post(self.__conn)

    # sObjectTypes can be 1 or a list, returns a single describe result or a list of them
    def describeSObjects(self, sObjectTypes):
        return DescribeSObjectsRequest(self.__serverUrl, self.sessionId, sObjectTypes).post(self.__conn)

    def describeGlobal(self):
        return AuthenticatedRequest(self.__serverUrl, self.sessionId, "describeGlobal").post(self.__conn)

    def describeLayout(self, sObjectType):
        return DescribeLayoutRequest(self.__serverUrl, self.sessionId, sObjectType).post(self.__conn)

    def describeTabs(self):
        return AuthenticatedRequest(self.__serverUrl, self.sessionId, "describeTabs").post(self.__conn, True)

    def getServerTimestamp(self):
        return str(AuthenticatedRequest(self.__serverUrl, self.sessionId, "getServerTimestamp").post(self.__conn)[_tPartnerNS.timestamp])

    def resetPassword(self, userId):
        return ResetPasswordRequest(self.__serverUrl, self.sessionId, userId).post(self.__conn)

    def setPassword(self, userId, password):
        SetPasswordRequest(self.__serverUrl, self.sessionId, userId, password).post(self.__conn)

    def getUserInfo(self):
        return AuthenticatedRequest(self.__serverUrl, self.sessionId, "getUserInfo").post(self.__conn)

    #def convertLead(self, convertLeads):

# fixed version of XmlGenerator, handles unqualified attributes correctly
class BeatBoxXmlGenerator(XMLGenerator):
    def __init__(self, destination, encoding):
        XMLGenerator.__init__(self, destination, encoding)

    def makeName(self, name):
        if name[0] is None:
            #if the name was not namespace-scoped, use the qualified part
            return name[1]
        # else try to restore the original prefix from the namespace
        return self._current_context[name[0]] + ":" + name[1]

    def startElementNS(self, name, qname, attrs):
        self._write(unicode('<' + self.makeName(name)))

        for pair in self._undeclared_ns_maps:
            self._write(unicode(' xmlns:%s="%s"' % pair))
        self._undeclared_ns_maps = []

        for (name, value) in attrs.items():
            self._write(unicode(' %s=%s' % (self.makeName(name), quoteattr(value))))
        self._write(unicode('>'))

# General purpose xml writer.
# Does a bunch of useful stuff above & beyond XmlGenerator
# TODO: What does it do, beyond XMLGenerator?
class XmlWriter:
    def __init__(self, doGzip):
        self.__buf = StringIO("")
        if doGzip:
            self.__gzip = gzip.GzipFile(mode='wb', fileobj=self.__buf)
            stm = self.__gzip
        else:
            stm = self.__buf
            self.__gzip = None
        self.xg = BeatBoxXmlGenerator(stm, "utf-8")
        self.xg.startDocument()
        self.__elems = []

    def startPrefixMapping(self, prefix, namespace):
        self.xg.startPrefixMapping(prefix, namespace)

    def endPrefixMapping(self, prefix):
        self.xg.endPrefixMapping(prefix)

    def startElement(self, namespace, name, attrs = _noAttrs):
        self.xg.startElementNS((namespace, name), name, attrs)
        self.__elems.append((namespace, name))

    # General Function for writing an XML Element.
    # Detects the type of the element, and handles each type appropriately.
    # i.e. If a list, then it encodes each element, if a dict, it writes an
    # embedded element.
    def writeElement(self, namespace, name, value, attrs = _noAttrs):
        if islst(value):
            for v in value:
                self.writeElement(namespace, name, v, attrs)
        elif isinstance(value, dict):
            self.startElement(namespace, name, attrs)
            # Type must always come first, even in embedded objects.
            type_entry = value['type']
            self.writeElement(namespace, 'type', type_entry, attrs)
            del value['type']
            for k, v in value.items():
                self.writeElement(namespace, k, v, attrs)
            self.endElement()
        else:
            self.startElement(namespace, name, attrs)
            self.characters(value)
            self.endElement()

    def endElement(self):
        e = self.__elems[-1];
        self.xg.endElementNS(e, e[1])
        del self.__elems[-1]

    def characters(self, s):
        # todo base64 ?
        if isinstance(s, datetime.datetime) or isinstance(s, datetime.date):
            s = s.isoformat()
        elif isinstance(s, (int, float, long)):
            s = str(s)
        self.xg.characters(s)

    def endDocument(self):
        self.xg.endDocument()
        if (self.__gzip != None):
            self.__gzip.close();
        return self.__buf.getvalue()

# exception class for soap faults
class SoapFaultError(Exception):
    def __init__(self, faultCode, faultString):
        self.faultCode = faultCode
        self.faultString = faultString

    def __str__(self):
        return repr(self.faultCode) + " " + repr(self.faultString)

class SessionTimeoutError(Exception):
    """
    SessionTimeouts are recoverable errors, merely needing the creation
    of a new connection, we create a new exception type, so these can
    be identified and handled seperately from SoapFaultErrors
    """
    def __init__(self, faultCode, faultString):
        self.faultCode = faultCode
        self.faultString = faultString

    def __str__(self):
        return repr(self.faultCode) + " " + repr(self.faultString)


# soap specific stuff ontop of XmlWriter
class SoapWriter(XmlWriter):
    def __init__(self):
        XmlWriter.__init__(self, gzipRequest)
        self.startPrefixMapping("s", _envNs)
        self.startPrefixMapping("p", _partnerNs)
        self.startPrefixMapping("o", _sobjectNs)
        self.startElement(_envNs, "Envelope")

    def endDocument(self):
        self.endElement()  # envelope
        self.endPrefixMapping("o")
        self.endPrefixMapping("p")
        self.endPrefixMapping("s")
        return XmlWriter.endDocument(self)

# processing for a single soap request / response
class SoapEnvelope:
    def __init__(self, serverUrl, operationName, clientId="BeatBox/" + __version__):
        self.serverUrl = serverUrl
        self.operationName = operationName
        self.clientId = clientId

    def writeHeaders(self, writer):
        pass

    def writeBody(self, writer):
        pass

    def makeEnvelope(self):
        s = SoapWriter()
        s.startElement(_envNs, "Header")
        s.characters("\n")
        s.startElement(_partnerNs, "CallOptions")
        s.writeElement(_partnerNs, "client", self.clientId)
        s.endElement()
        s.characters("\n")
        self.writeHeaders(s)
        s.endElement()  # Header
        s.startElement(_envNs, "Body")
        s.characters("\n")
        s.startElement(_partnerNs, self.operationName)
        self.writeBody(s)
        s.endElement()  # operation
        s.endElement()  # body
        return s.endDocument()

    # does all the grunt work:
    # * serializes the request
    # * makes a http request
    # * passes the response to tramp
    # * checks for soap fault
    #  returns the relevant result from the body child
    # TODO: check for mU='1' headers
    def post(self, conn=None, alwaysReturnList=False):
        headers = { "User-Agent": "Pyforce/{0}".format(__version__),
                "SOAPAction": '""',
                "Content-Type": "text/xml; charset=utf-8" }
        if gzipResponse:
            headers['accept-encoding'] = 'gzip'
        if gzipRequest:
            headers['content-encoding'] = 'gzip'
        close = False
        (scheme, host, path, params, query, frag) = urlparse(self.serverUrl)
        max_attempts = 3
        response = None
        attempt = 1
        while not response and attempt <= max_attempts:
            try:
                if conn == None:
                    conn = makeConnection(scheme, host)
                    close = True
                conn.request("POST", path, self.makeEnvelope(), headers)
                response = conn.getresponse()
                rawResponse = response.read()
            except (httplib.HTTPException, socket.error):
                if conn != None:
                    conn.close()
                    conn = None
                    response = None
                attempt += 1
        if not response:
            raise RuntimeError, 'No response from Salesforce'

        if response.getheader('content-encoding','') == 'gzip':
            rawResponse = gzip.GzipFile(fileobj=StringIO(rawResponse)).read()
        if close:
            conn.close()
        tramp = xmltramp.parse(rawResponse)
        try:
            faultString = str(tramp[_tSoapNS.Body][_tSoapNS.Fault].faultstring)
            faultCode   = str(tramp[_tSoapNS.Body][_tSoapNS.Fault].faultcode).split(':')[-1]
            if faultCode == 'INVALID_SESSION_ID':
                raise SessionTimeoutError(faultCode, faultString)
            else:
                raise SoapFaultError(faultCode, faultString)
        except KeyError:
            pass
        # first child of body is XXXXResponse
        result = tramp[_tSoapNS.Body][0]
        # it contains either a single child, or for a batch call multiple children
        if alwaysReturnList or len(result) > 1:
            return result[:]
        else:
            return result[0]


class LoginRequest(SoapEnvelope):
    def __init__(self, serverUrl, username, password):
        SoapEnvelope.__init__(self, serverUrl, "login")
        self.__username = username
        self.__password = password

    def writeBody(self, s):
        s.writeElement(_partnerNs, "username", self.__username)
        s.writeElement(_partnerNs, "password", self.__password)


# base class for all methods that require a sessionId
class AuthenticatedRequest(SoapEnvelope):
    def __init__(self, serverUrl, sessionId, operationName):
        SoapEnvelope.__init__(self, serverUrl, operationName)
        self.sessionId = sessionId

    def writeHeaders(self, s):
        s.startElement(_partnerNs, "SessionHeader")
        s.writeElement(_partnerNs, "sessionId", self.sessionId)
        s.endElement()

    def writeSObjects(self, s, sObjects, elemName="sObjects"):
        if islst(sObjects):
            for o in sObjects:
                self.writeSObjects(s, o, elemName)
        else:
            s.startElement(_partnerNs, elemName)
            # type has to go first
            s.writeElement(_sobjectNs, "type", sObjects['type'])
            for fn in sObjects.keys():
                if (fn != 'type'):
                    s.writeElement(_sobjectNs, fn, sObjects[fn])
            s.endElement()


class QueryOptionsRequest(AuthenticatedRequest):
    def __init__(self, serverUrl, sessionId, batchSize, operationName):
        AuthenticatedRequest.__init__(self, serverUrl, sessionId, operationName)
        self.batchSize = batchSize

    def writeHeaders(self, s):
        AuthenticatedRequest.writeHeaders(self, s)
        s.startElement(_partnerNs, "QueryOptions")
        s.writeElement(_partnerNs, "batchSize", self.batchSize)
        s.endElement()


class QueryRequest(QueryOptionsRequest):
    def __init__(self, serverUrl, sessionId, batchSize, soql):
        QueryOptionsRequest.__init__(self, serverUrl, sessionId, batchSize, "query")
        self.__query = soql

    def writeBody(self, s):
        s.writeElement(_partnerNs, "queryString", self.__query)


class QueryMoreRequest(QueryOptionsRequest):
    def __init__(self, serverUrl, sessionId, batchSize, queryLocator):
        QueryOptionsRequest.__init__(self, serverUrl, sessionId, batchSize, "queryMore")
        self.__queryLocator = queryLocator

    def writeBody(self, s):
        s.writeElement(_partnerNs, "queryLocator", self.__queryLocator)


class SearchRequest(QueryOptionsRequest):
    def __init__(self, serverUrl, sessionId, batchSize, sosl):
        QueryOptionsRequest.__init__(self, serverUrl, sessionId, batchSize, "search")
        self.__search = sosl

    def writeBody(self, s):
        s.writeElement(_partnerNs, "searchString", self.__search)


class GetUpdatedRequest(AuthenticatedRequest):
    def __init__(self, serverUrl, sessionId, sObjectType, start, end, operationName="getUpdated"):
        AuthenticatedRequest.__init__(self, serverUrl, sessionId, operationName)
        self.__sObjectType = sObjectType
        self.__start = start;
        self.__end = end;

    def writeBody(self, s):
        s.writeElement(_partnerNs, "sObjectType", self.__sObjectType)
        s.writeElement(_partnerNs, "startDate", self.__start)
        s.writeElement(_partnerNs, "endDate", self.__end)


class GetDeletedRequest(GetUpdatedRequest):
    def __init__(self, serverUrl, sessionId, sObjectType, start, end):
        GetUpdatedRequest.__init__(self, serverUrl, sessionId, sObjectType, start, end, "getDeleted")


class UpsertRequest(AuthenticatedRequest):
    def __init__(self, serverUrl, sessionId, externalIdName, sObjects):
        AuthenticatedRequest.__init__(self, serverUrl, sessionId, "upsert")
        self.__externalIdName = externalIdName
        self.__sObjects = sObjects

    def writeBody(self, s):
        s.writeElement(_partnerNs, "externalIDFieldName", self.__externalIdName)
        self.writeSObjects(s, self.__sObjects)


class UpdateRequest(AuthenticatedRequest):
    def __init__(self, serverUrl, sessionId, sObjects, operationName="update"):
        AuthenticatedRequest.__init__(self, serverUrl, sessionId, operationName)
        self.__sObjects = sObjects

    def writeBody(self, s):
        self.writeSObjects(s, self.__sObjects)


class CreateRequest(UpdateRequest):
    def __init__(self, serverUrl, sessionId, sObjects):
        UpdateRequest.__init__(self, serverUrl, sessionId, sObjects, "create")


class DeleteRequest(AuthenticatedRequest):
    def __init__(self, serverUrl, sessionId, ids):
        AuthenticatedRequest.__init__(self, serverUrl, sessionId, "delete")
        self.__ids = ids;

    def writeBody(self, s):
        s.writeElement(_partnerNs, "id", self.__ids)


class RetrieveRequest(AuthenticatedRequest):
    def __init__(self, serverUrl, sessionId, fields, sObjectType, ids):
        AuthenticatedRequest.__init__(self, serverUrl, sessionId, "retrieve")
        self.__fields = fields
        self.__sObjectType = sObjectType
        self.__ids = ids

    def writeBody(self, s):
        s.writeElement(_partnerNs, "fieldList", self.__fields)
        s.writeElement(_partnerNs, "sObjectType", self.__sObjectType);
        s.writeElement(_partnerNs, "ids", self.__ids)


class ResetPasswordRequest(AuthenticatedRequest):
    def __init__(self, serverUrl, sessionId, userId):
        AuthenticatedRequest.__init__(self, serverUrl, sessionId, "resetPassword")
        self.__userId = userId

    def writeBody(self, s):
        s.writeElement(_partnerNs, "userId", self.__userId)


class SetPasswordRequest(AuthenticatedRequest):
    def __init__(self, serverUrl, sessionId, userId, password):
        AuthenticatedRequest.__init__(self, serverUrl, sessionId, "setPassword")
        self.__userId = userId
        self.__password = password

    def writeBody(self, s):
        s.writeElement(_partnerNs, "userId", self.__userId)
        s.writeElement(_partnerNs, "password", self.__password)


class DescribeSObjectsRequest(AuthenticatedRequest):
    def __init__(self, serverUrl, sessionId, sObjectTypes):
        AuthenticatedRequest.__init__(self, serverUrl, sessionId, "describeSObjects")
        self.__sObjectTypes = sObjectTypes

    def writeBody(self, s):
        s.writeElement(_partnerNs, "sObjectType", self.__sObjectTypes)


class DescribeLayoutRequest(AuthenticatedRequest):
    def __init__(self, serverUrl, sessionId, sObjectType):
        AuthenticatedRequest.__init__(self, serverUrl, sessionId, "describeLayout")
        self.__sObjectType = sObjectType

    def writeBody(self, s):
        s.writeElement(_partnerNs, "sObjectType", self.__sObjectType)
