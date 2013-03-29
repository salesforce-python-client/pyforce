import unittest
import pyforce
import sfconfig
import datetime
partnerns = pyforce._tPartnerNS
svc = pyforce.XMLClient()

class TestBeatbox(unittest.TestCase):

    def setUp(self):
        svc.login(sfconfig.USERNAME, sfconfig.PASSWORD)
        self._todelete = list()

    def tearDown(self):
        for id in self._todelete:
            res = svc.delete(id)

    def testCreate(self):
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create([data])
        self.assertEqual(str(res[partnerns.success]), 'true')
        id = str(res[partnerns.id])
        self._todelete.append(id)
        contact = svc.retrieve('LastName, FirstName, Phone, Email', 'Contact',
            [id])
        for k in ['LastName', 'FirstName', 'Phone', 'Email']:
            self.assertEqual(
                data[k], str(contact[getattr(pyforce._tSObjectNS, k)]))


    def testUpdate(self):
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Email='john@doe.com',
            )
        res = svc.create([data])
        self.assertEqual(str(res[partnerns.success]), 'true')
        id = str(res[partnerns.id])
        self._todelete.append(id)
        contact = svc.retrieve('Email', 'Contact', [id])
        self.assertEqual(
            str(contact[pyforce._tSObjectNS.Email]), data['Email'])
        updata = dict(type='Contact',
            Id=id,
            Email='jd@doe.com'
            )
        res = svc.update(updata)
        self.assertEqual(str(res[partnerns.success]), 'true')
        contact = svc.retrieve('LastName, FirstName, Email', 'Contact',
            [id])
        for k in ['LastName', 'FirstName', ]:
            self.assertEqual(
                data[k], str(contact[getattr(pyforce._tSObjectNS, k)]))
        self.assertEqual(
            str(contact[pyforce._tSObjectNS.Email]), updata['Email'])

    def testQuery(self):
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create([data])
        self.assertEqual(str(res[partnerns.success]), 'true')
        self._todelete.append(str(res[partnerns.id]))
        data2 = dict(type='Contact',
            LastName='Doe',
            FirstName='Jane',
            Phone='123-456-7890',
            Email='jane@doe.com',
            Birthdate = datetime.date(1972, 10, 15)
            )
        res = svc.create([data2])
        self.assertEqual(str(res[partnerns.success]), 'true')
        janeid = str(res[partnerns.id])
        self._todelete.append(janeid)
        query = ("select LastName, FirstName, Phone, Email, Birthdate "
            "from Contact where LastName = 'Doe'")
        res = svc.query(query)
        self.assertEqual(int(str(res[partnerns.size])), 2)
        query = ("select Id, LastName, FirstName, Phone, Email, Birthdate "
            "from Contact where LastName = 'Doe' and FirstName = 'Jane'")
        res = svc.query(query)
        self.assertEqual(int(str(res[partnerns.size])), 1)
        records = res[partnerns.records:]
        self.assertEqual(
            janeid, str(records[0][pyforce._tSObjectNS.Id]))

    def testSearch(self):
        sosl = 'find {barr} in ALL FIELDS returning Contact(Id, LastName, FirstName, Phone, Email, Birthdate)'
        res = svc.search(sosl)
        self.assertEqual(len(res), 1)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestBeatbox),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

