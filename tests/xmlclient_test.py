from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import os
import unittest
from time import sleep

import pyforce

partnerns = pyforce.pyclient._tPartnerNS
sobjectns = pyforce.pyclient._tSObjectNS
DEFAULT_HOSTNAME = "test.salesforce.com"
DELAY_RETRY = 10
DELAY_SEC = 2


class TestBeatbox(unittest.TestCase):

    def setUp(self):
        hostname = os.getenv('SF_HOSTNAME', DEFAULT_HOSTNAME)
        server_url = "https://{}/services/Soap/u/20.0".format(hostname)
        self.svc = pyforce.XMLClient(server_url)
        password = os.getenv('SF_PASSWORD') + os.getenv('SF_SECTOKEN', '')
        self.svc.login(os.getenv('SF_USERNAME'), password)
        self._todelete = list()

    def tearDown(self):
        for id in self._todelete:
            self.svc.delete(id)

    def testCreate(self):
        data = dict(
            type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate=datetime.date(1970, 1, 4),
        )
        res = self.svc.create([data])
        self.assertEqual(str(res[partnerns.success]), 'true')
        id = str(res[partnerns.id])
        self._todelete.append(id)
        contact = self.svc.retrieve(
            'LastName, FirstName, Phone, Email',
            'Contact',
            [id],
        )
        for k in ['LastName', 'FirstName', 'Phone', 'Email']:
            self.assertEqual(data[k], str(contact[getattr(sobjectns, k)]))

    def testUpdate(self):
        data = dict(
            type='Contact',
            LastName='Doe',
            FirstName='John',
            Email='john@doe.com',
        )
        res = self.svc.create([data])
        self.assertEqual(str(res[partnerns.success]), 'true')
        id = str(res[partnerns.id])
        self._todelete.append(id)
        contact = self.svc.retrieve('Email', 'Contact', [id])
        self.assertEqual(
            str(contact[sobjectns.Email]), data['Email'])
        updata = dict(
            type='Contact',
            Id=id,
            Email='jd@doe.com',
        )
        res = self.svc.update(updata)
        self.assertEqual(str(res[partnerns.success]), 'true')
        contact = self.svc.retrieve(
            'LastName, FirstName, Email',
            'Contact',
            [id],
        )
        for k in ['LastName', 'FirstName', ]:
            self.assertEqual(
                data[k],
                str(contact[getattr(sobjectns, k)]),
            )
        self.assertEqual(
            str(contact[sobjectns.Email]), updata['Email'])

    def testQuery(self):
        data = dict(
            type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate=datetime.date(1970, 1, 4),
        )
        res = self.svc.create([data])
        self.assertEqual(str(res[partnerns.success]), 'true')
        self._todelete.append(str(res[partnerns.id]))
        data2 = dict(
            type='Contact',
            LastName='Doe',
            FirstName='Jane',
            Phone='123-456-7890',
            Email='jane@doe.com',
            Birthdate=datetime.date(1972, 10, 15),
        )
        res = self.svc.create([data2])
        self.assertEqual(str(res[partnerns.success]), 'true')
        janeid = str(res[partnerns.id])
        self._todelete.append(janeid)
        query = ("select LastName, FirstName, Phone, Email, Birthdate "
                 "from Contact where LastName = 'Doe'")
        res = self.svc.query(query)
        self.assertEqual(int(str(res[partnerns.size])), 2)
        query = ("select Id, LastName, FirstName, Phone, Email, Birthdate "
                 "from Contact where LastName = 'Doe' and FirstName = 'Jane'")
        res = self.svc.query(query)
        self.assertEqual(int(str(res[partnerns.size])), 1)
        records = res[partnerns.records, ]
        self.assertEqual(
            janeid, str(records[0][sobjectns.Id]))

    def testSearch(self):
        data = dict(
            type='Contact',
            LastName='LongLastName',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate=datetime.date(1970, 1, 4),
        )
        res = self.svc.create([data])
        self.assertEqual(str(res[partnerns.success]), 'true')
        self._todelete.append(str(res[partnerns.id]))

        # Requires some delay for indexing
        for _ in range(DELAY_RETRY):
            sleep(DELAY_SEC)
            res = self.svc.search(
                "FIND {Long} in ALL FIELDS RETURNING "
                "Contact(Id, LastName, FirstName, Phone, Email, Birthdate)"
            )
            if len(res) > 0:
                break
        self.assertEqual(len(res), 1)

    @unittest.skip("Email is not working...")
    def testSendSimpleEmail(self):
        testemail = {
            'subject': (
                'pyforce test_xmlclient.py testSendSimpleEmail of '
                'Salesforce sendEmail()'
            ),
            'saveAsActivity': False,
            'toAddresses': str(self.svc.getUserInfo()['userEmail']),
            'plainTextBody': (
                'This is a test email message with HTML markup.\n\n'
                'You are currently looking at the plain-text body, '
                'but the message is sent in both forms.'
            ),
        }
        res = self.svc.sendEmail([testemail])
        self.assertEqual(str(res[partnerns.success]), 'true')

    @unittest.skip("Email is not working...")
    def testSendEmailMissingFields(self):
        testemail = {
            'toAddresses': str(self.svc.getUserInfo()['userEmail']),
        }
        res = self.svc.sendEmail([testemail])
        self.assertEqual(str(res[partnerns.success]), 'false')
        self.assertEqual(
            str(res[partnerns.errors][partnerns.statusCode]),
            'REQUIRED_FIELD_MISSING',
        )

    @unittest.skip("Email is not working...")
    def testSendHTMLEmailWithAttachment(self):
        solid_logo = {
            'body': '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',  # NOQA
            'contentType': 'image/png',
            'fileName': 'salesforce_logo.png',
            'inline': True
        }
        testemail = {
            'subject': (
                'pyforce test_xmlclient.py testSendHTMLEmailWithAttachment '
                'of Salesforce sendEmail()'
            ),
            'useSignature': True,
            'saveAsActivity': False,
            'toAddresses': str(self.svc.getUserInfo()['userEmail']),
            'plainTextBody': (
                'This is a test email message with HTML markup.\n\n'
                'You are currently looking at the plain-text body, '
                'but the message is sent in both forms.'
            ),
            'htmlBody': '<html><head><meta http-equiv="content-type" content="text/html; charset=utf-8"><body><h1>This is a test email message with HTML markup.</h1>\n\n<p>You are currently looking at the <i>HTML</i> body, but the message is sent in both forms.</p></body></html>',  # NOQA
            'inReplyTo': '<1234567890123456789%example@example.com>',
            'references': '<1234567890123456789%example@example.com>',
            'fileAttachments': [solid_logo]
        }
        res = self.svc.sendEmail([testemail])
        self.assertEqual(str(res[partnerns.success]), 'true')

    def testLogout(self):
        """Logout and verify that the previous sessionId longer works."""
        # from ipdb import set_trace; set_trace()
        result = self.svc.getUserInfo()
        self.assertTrue(hasattr(result, 'userId'))
        response = self.svc.logout()
        self.assertEqual(
            response._name,
            partnerns.logoutResponse,
            "Response {} was not {}".format(
                response._name,
                partnerns.logoutResponse,
            ),
        )
        with self.assertRaises(pyforce.xmlclient.SessionTimeoutError) as cm:
            # Sometimes this doesn't work on the first try. Flakey...
            for _ in range(DELAY_RETRY):
                sleep(DELAY_SEC)
                result = self.svc.getUserInfo()
        self.assertEqual(
            cm.exception.faultCode,
            'INVALID_SESSION_ID',
            "Session didn't fail with INVALID_SESSION_ID.",
        )


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestBeatbox),
    ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
