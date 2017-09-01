import datetime
import gc
import unittest
from time import time
from types import ListType, TupleType

import sfconfig

import pyforce

BENCHMARK_REPS = 1
def benchmark(func):
    def benchmarked_func(self):
        # temporarily disable garbage collection
        gc.disable()
        t0 = time()
        for i in xrange(0, BENCHMARK_REPS):
            func(self)
        t1 = time()
        gc.enable()
        elapsed = t1 - t0
        print "\n%s: %s\n" % (func.__name__, elapsed)
    return benchmarked_func

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.svc = svc = pyforce.PythonClient(serverUrl='https://www.salesforce.com/services/Soap/u/15.0')
        svc.login(sfconfig.USERNAME, sfconfig.PASSWORD)
        self._todelete = list()

    def tearDown(self):
        svc = self.svc
        ids = self._todelete
        if ids:
            while len(ids) > 200:
                svc.delete(ids[:200])
                ids = ids[200:]
            if ids:
                svc.delete(ids)
        self._todelete = list()

    @benchmark
    def testDescribeSObjects(self):
        svc = self.svc
        globalres = svc.describeGlobal()
        types = globalres['types']
        res = svc.describeSObjects(types[0])
        self.assertEqual(type(res), ListType)
        self.assertEqual(len(res), 1)
        res = svc.describeSObjects(types[:100])
        self.assertEqual(len(types[:100]), len(res))

    @benchmark
    def testCreate(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create([data])
        self.failUnless(type(res) in (ListType, TupleType))
        self.failUnless(len(res) == 1)
        self.failUnless(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, FirstName, Phone, Email, Birthdate',
            'Contact', [id])
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        for k in ['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate']:
            self.assertEqual(
                data[k], contact[k])
                
    @benchmark
    def testQuery(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create([data])
        self._todelete.append(res[0]['id'])
        data2 = dict(type='Contact',
            LastName='Doe',
            FirstName='Jane',
            Phone='123-456-7890',
            Email='jane@doe.com',
            Birthdate = datetime.date(1972, 10, 15)
            )
        res = svc.create([data2])
        janeid = res[0]['id']
        self._todelete.append(janeid)
        res = svc.query('LastName, FirstName, Phone, Email, Birthdate',
                'Contact', "LastName = 'Doe'")
        self.assertEqual(res['size'], 2)
        res = svc.query('Id, LastName, FirstName, Phone, Email, Birthdate',
                'Contact', "LastName = 'Doe' and FirstName = 'Jane'")
        self.assertEqual(res['size'], 1)
        self.assertEqual(res['records'][0]['Id'], janeid)
        self.tearDown()

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtils),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
