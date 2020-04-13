from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import gc
import os
import unittest
from time import time

import six

import pyforce

BENCHMARK_REPS = 1

DEFAULT_HOSTNAME = "test.salesforce.com"


def benchmark(func):
    def benchmarked_func(self):
        # temporarily disable garbage collection
        gc.disable()
        t0 = time()
        for i in six.moves.xrange(0, BENCHMARK_REPS):
            func(self)
        t1 = time()
        gc.enable()
        elapsed = t1 - t0
        print("\n%s: %s\n" % (func.__name__, elapsed))
    return benchmarked_func


class TestUtils(unittest.TestCase):

    def setUp(self):
        hostname = os.getenv('SF_HOSTNAME', DEFAULT_HOSTNAME)
        server_url = "https://{}/services/Soap/u/20.0".format(hostname)
        self.svc = pyforce.PythonClient(serverUrl=server_url)
        password = os.getenv('SF_PASSWORD') + os.getenv('SF_SECTOKEN', '')
        self.svc.login(os.getenv('SF_USERNAME'), password)
        self._todelete = list()

    def tearDown(self):
        ids = self._todelete
        if ids:
            while len(ids) > 200:
                self.svc.delete(ids[:200])
                ids = ids[200:]
            if ids:
                self.svc.delete(ids)
        self._todelete = list()

    @benchmark
    def testDescribeSObjects(self):
        globalres = self.svc.describeGlobal()
        types = globalres['types']
        res = self.svc.describeSObjects(types[0])
        self.assertEqual(type(res), list)
        self.assertEqual(len(res), 1)
        res = self.svc.describeSObjects(types[:100])
        self.assertEqual(len(types[:100]), len(res))

    @benchmark
    def testCreate(self):
        data = dict(type='Contact',
                    LastName='Doe',
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=datetime.date(1970, 1, 4)
                    )
        res = self.svc.create([data])
        self.assertTrue(type(res) in (list, tuple))
        self.assertTrue(len(res) == 1)
        self.assertTrue(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve(
            'LastName, FirstName, Phone, Email, Birthdate',
            'Contact',
            [id],
        )
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        for k in ['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate']:
            self.assertEqual(
                data[k], contact[k])

    @benchmark
    def testQuery(self):
        data = dict(type='Contact',
                    LastName='Doe',
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=datetime.date(1970, 1, 4)
                    )
        res = self.svc.create([data])
        self._todelete.append(res[0]['id'])
        data2 = dict(type='Contact',
                     LastName='Doe',
                     FirstName='Jane',
                     Phone='123-456-7890',
                     Email='jane@doe.com',
                     Birthdate=datetime.date(1972, 10, 15)
                     )
        res = self.svc.create([data2])
        janeid = res[0]['id']
        self._todelete.append(janeid)
        res = self.svc.query(
            'LastName, FirstName, Phone, Email, Birthdate',
            'Contact',
            "LastName = 'Doe'",
        )
        self.assertEqual(len(res), 2)
        self.assertEqual(res['size'], 2)
        self.assertEqual(res.size, 2)
        res = self.svc.query(
            'Id, LastName, FirstName, Phone, Email, Birthdate',
            'Contact',
            "LastName = 'Doe' and FirstName = 'Jane'",
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['Id'], janeid)
        self.tearDown()


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtils),
    ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
