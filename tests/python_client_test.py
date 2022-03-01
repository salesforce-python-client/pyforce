from __future__ import absolute_import
from __future__ import unicode_literals

import datetime
import os
import unittest
from time import sleep

from six import string_types

import pyforce
from pyforce import SoapFaultError
from pyforce.pyclient import _prepareSObjects


DEFAULT_HOSTNAME = "test.salesforce.com"
DELAY_RETRY = 10
DELAY_SEC = 2


class TestUtils(unittest.TestCase):

    def setUp(self):
        hostname = os.getenv('SF_HOSTNAME', DEFAULT_HOSTNAME)
        server_url = "https://{}/services/Soap/u/20.0".format(hostname)
        self.svc = self.svc = pyforce.PythonClient(serverUrl=server_url)
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

    def testDescribeGlobal(self):
        res = self.svc.describeGlobal()
        self.assertEqual(type(res), dict)
        self.assertTrue(isinstance(res['encoding'], string_types))
        self.assertTrue(isinstance(res['maxBatchSize'], int))
        self.assertTrue(isinstance(res['types'], list))
        self.assertTrue(len(res['sobjects']) > 0)
        # BBB for API < 17.0
        self.assertTrue(len(res['types']) > 0)

    def testDescribeSObjects(self):
        globalres = self.svc.describeGlobal()
        types = globalres['types'][:100]
        res = self.svc.describeSObjects(types[0])
        self.assertEqual(type(res), list)
        self.assertEqual(len(res), 1)
        res = self.svc.describeSObjects(types)
        self.assertEqual(len(types), len(res))

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

    def testSetIntegerField(self):
        # Passes when you feed it floats, even if salesforce field is defined
        # for 0 decimal places.  Lack of data validation in SF?
        testField = 'Favorite_Integer__c'
        data = dict(
            type='Contact',
            LastName='Doe',
            FirstName='John',
            Favorite_Integer__c=-25,
        )
        res = self.svc.create([data])
        self.assertTrue(type(res) in (list, tuple))
        self.assertTrue(len(res) == 1)
        self.assertTrue(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve(
            'LastName, FirstName, Favorite_Integer__c',
            'Contact',
            [id],
        )
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        self.assertEqual(data[testField], contact[testField])

    def testSetFloatField(self):
        # this fails when you have a large amount (I didn't test the #)
        # of decimal places.
        testField = 'Favorite_Float__c'
        data = dict(type='Contact',
                    LastName='Doe',
                    FirstName='John',
                    Favorite_Float__c=-1.999888777
                    )
        res = self.svc.create([data])
        self.assertTrue(type(res) in (list, tuple))
        self.assertTrue(len(res) == 1)
        self.assertTrue(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve(
            'LastName, FirstName, Favorite_Float__c',
            'Contact',
            [id],
        )
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        self.assertEqual(data[testField], contact[testField])

    def testCreatePickListMultiple(self):

        data = dict(
            type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate=datetime.date(1970, 1, 4),
            Favorite_Fruit__c=["Apple", "Orange", "Pear"],
        )
        res = self.svc.create([data])
        self.assertTrue(type(res) in (list, tuple))
        self.assertTrue(len(res) == 1)
        self.assertTrue(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve(
            'LastName, FirstName, Phone, Email, Birthdate, Favorite_Fruit__c',
            'Contact',
            [id],
        )
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        for k in [
            'LastName',
            'FirstName',
            'Phone',
            'Email',
            'Birthdate',
            'Favorite_Fruit__c',
        ]:
            self.assertEqual(data[k], contact[k])

    #def testCreatePickListMultipleWithInvalid(self):
        #""" This fails, and I guess it should(?)
        #     SF doesn't enforce vocabularies, appearently """

        #data = dict(type='Contact',
            #LastName='Doe',
            #FirstName='John',
            #Phone='123-456-7890',
            #Email='john@doe.com',
            #Birthdate = datetime.date(1970, 1, 4),
            #Favorite_Fruit__c = ["Apple","Orange","Pear","RottenFruit"]
            #)
        #res = self.svc.create([data])
        #self.assertTrue(type(res) in (list, tuple))
        #self.assertTrue(len(res) == 1)
        #self.assertTrue(res[0]['success'])
        #id = res[0]['id']
        #self._todelete.append(id)
        #contacts = self.svc.retrieve('LastName, FirstName, Phone, Email, Birthdate, \
            #Favorite_Fruit__c', 'Contact', [id])
        #self.assertEqual(len(contacts), 1)
        #contact = contacts[0]
        #self.assertNotEqual(data['Favorite_Fruit__c'], contact['Favorite_Fruit__c'])
        #self.assertEqual(len(contact['Favorite_Fruit__c']),3)
        #for k in ['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate', 'Favorite_Fruit__c']:
            #self.assertEqual(
            #data[k], contact[k])

    def testFailedCreate(self):
        data = dict(
            type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate='foo',
        )
        self.assertRaises(SoapFaultError, self.svc.create, data)

    def testRetrieve(self):
        data = dict(
            type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate=datetime.date(1970, 1, 4),
        )
        res = self.svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        typedesc = self.svc.describeSObjects('Contact')[0]
        fieldnames = list()
        fields = typedesc.fields.values()
        fieldnames = [f.name for f in fields]
        fieldnames = ', '.join(fieldnames)
        contacts = self.svc.retrieve(fieldnames, 'Contact', [id])
        self.assertEqual(len(contacts), 1)

    def testRetrieveDeleted(self):
        data = dict(type='Contact',
                    LastName='Doe',
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=datetime.date(1970, 1, 4)
                    )
        res = self.svc.create(data)
        id = res[0]['id']
        self.svc.delete(id)
        typedesc = self.svc.describeSObjects('Contact')[0]
        fieldnames = list()
        fields = typedesc.fields.values()
        fieldnames = [f.name for f in fields]
        fieldnames = ', '.join(fieldnames)
        contacts = self.svc.retrieve(fieldnames, 'Contact', [id])
        self.assertEqual(len(contacts), 0)

    def testDelete(self):
        data = dict(type='Contact',
                    LastName='Doe',
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=datetime.date(1970, 1, 4)
                    )
        res = self.svc.create([data])
        id = res[0]['id']
        res = self.svc.delete([id])
        self.assertTrue(res[0]['success'])
        contacts = self.svc.retrieve('LastName', 'Contact', [id])
        self.assertEqual(len(contacts), 0)

    def testUpdate(self):
        originaldate = datetime.date(1970, 1, 4)
        newdate = datetime.date(1970, 1, 5)
        lastname = 'Doe'
        data = dict(type='Contact',
                    LastName=lastname,
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=originaldate
                    )
        res = self.svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve('LastName, Birthdate', 'Contact', [id])
        self.assertEqual(contacts[0]['Birthdate'], originaldate)
        self.assertEqual(contacts[0]['LastName'], lastname)
        data = dict(type='Contact',
                    Id=id,
                    Birthdate=newdate)
        self.svc.update(data)
        contacts = self.svc.retrieve('LastName, Birthdate', 'Contact', [id])
        self.assertEqual(contacts[0]['Birthdate'], newdate)
        self.assertEqual(contacts[0]['LastName'], lastname)

    def testShrinkMultiPicklist(self):
        originalList = ["Pear", "Apple"]
        newList = ["Pear", ]
        lastname = 'Doe'
        data = dict(type='Contact',
                    LastName=lastname,
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Favorite_Fruit__c=originalList
                    )
        res = self.svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve(
            'LastName, Favorite_Fruit__c',
            'Contact',
            [id],
        )
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']), 2)
        data = dict(type='Contact',
                    Id=id,
                    Favorite_Fruit__c=newList)
        self.svc.update(data)
        contacts = self.svc.retrieve(
            'LastName, Favorite_Fruit__c',
            'Contact',
            [id],
        )
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']), 1)

    def testGrowMultiPicklist(self):
        originalList = ["Pear", "Apple"]
        newList = ["Pear", "Apple", "Orange"]
        lastname = 'Doe'
        data = dict(type='Contact',
                    LastName=lastname,
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Favorite_Fruit__c=originalList
                    )
        res = self.svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve(
            'LastName, Favorite_Fruit__c',
            'Contact',
            [id],
        )
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']), 2)
        data = dict(type='Contact',
                    Id=id,
                    Favorite_Fruit__c=newList)
        self.svc.update(data)
        contacts = self.svc.retrieve(
            'LastName, Favorite_Fruit__c',
            'Contact',
            [id],
        )
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']), 3)

    def testUpdateDeleted(self):
        originaldate = datetime.date(1970, 1, 4)
        newdate = datetime.date(1970, 1, 5)
        lastname = 'Doe'
        data = dict(type='Contact',
                    LastName=lastname,
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=originaldate
                    )
        res = self.svc.create(data)
        id = res[0]['id']
        self.svc.delete(id)
        contacts = self.svc.retrieve('LastName, Birthdate', 'Contact', [id])
        self.assertEqual(len(contacts), 0)
        data = dict(type='Contact',
                    Id=id,
                    Birthdate=newdate)
        res = self.svc.update(data)
        self.assertTrue(not res[0]['success'])
        self.assertTrue(len(res[0]['errors']) > 0)

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
        res = self.svc.query("SELECT LastName, FirstName, Phone, Email, Birthdate FROM Contact WHERE LastName = 'Doe'")
        self.assertEqual(len(res), 2)
        res = self.svc.query("SELECT Id, LastName, FirstName, Phone, Email, Birthdate FROM Contact WHERE LastName = 'Doe' and FirstName = 'Jane'")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['Id'], janeid)

    def testBackwardsCompatibleQuery(self):
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
        # conditional expression as positional arg
        res = self.svc.query(
            'LastName, FirstName, Phone, Email, Birthdate',
            'Contact',
            "LastName = 'Doe'",
        )
        self.assertEqual(len(res), 2)
        # conditional expression as *empty* positional arg
        res = self.svc.query('LastName', 'Contact', '')
        self.assertTrue(len(res) > 0)
        # conditional expression as kwarg
        res = self.svc.query(
            'Id, LastName, FirstName, Phone, Email, Birthdate',
            'Contact',
            conditionalExpression="LastName = 'Doe' and FirstName = 'Jane'",
        )
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0]['Id'], janeid)

    def testTypeDescriptionsCache(self):
        # patch describeSObjects to make a record when it is called
        calls = []
        standard_describeSObjects = pyforce.PythonClient.describeSObjects

        def patched_describeSObjects(self, sObjectTypes):
            calls.append(sObjectTypes)
            return standard_describeSObjects(self, sObjectTypes)
        pyforce.PythonClient.describeSObjects = patched_describeSObjects

        self.svc.cacheTypeDescriptions = True

        # should get called the first time
        self.svc.query('SELECT Id FROM Contact')
        self.assertEqual(calls, [['Contact']])
        # but not the second time
        self.svc.query('SELECT Id FROM Contact')
        self.assertEqual(calls, [['Contact']])

        # if we flush the cache, it should get called again
        self.svc.flushTypeDescriptionsCache()
        self.svc.query('SELECT Id FROM Contact')
        self.assertEqual(calls, [['Contact'], ['Contact']])

        # clean up
        self.svc.cacheTypeDescriptions = False

    def testChildToParentMultiQuery(self):
        account_data = dict(
            type='Account',
            Name='ChildTestAccount',
            AccountNumber='987654321',
            Site='www.testsite.com',
        )
        account = self.svc.create([account_data])
        self._todelete.append(account[0]['id'])

        contact_data = dict(
            type='Contact',
            LastName='TestLastName',
            FirstName='TestFirstName',
            Phone='123-456-7890',
            AccountID=account[0]['id'],
            Email='testfirstname@testlastname.com',
            Birthdate=datetime.date(1965, 1, 5),
        )
        contact = self.svc.create([contact_data])
        self._todelete.append(contact[0]['id'])

        query_res = self.svc.query(
            "Id, LastName, FirstName, Account.Site, Account.AccountNumber",
            "Contact",
            "Phone='123-456-7890'",
        )

        self.assertEqual(query_res.size, 1)
        rr = query_res.records[0]
        self.assertEqual(rr.type, 'Contact')
        map(
            self.assertEqual,
            [
                rr.Id,
                rr.LastName,
                rr.FirstName,
                rr.Account.Site,
                rr.Account.AccountNumber,
            ],
            [
                contact[0]['id'],
                contact_data['LastName'],
                contact_data['FirstName'],
                account_data['Site'],
                account_data['AccountNumber'],
            ],
        )

    def testChildToParentMultiQuery2(self):
        paccount_data = dict(type='Account',
                             Name='ParentTestAccount',
                             AccountNumber='123456789',
                             Site='www.testsite.com',
                             )
        paccount = self.svc.create([paccount_data])
        self._todelete.append(paccount[0]['id'])

        caccount_data = dict(type='Account',
                             Name='ChildTestAccount',
                             AccountNumber='987654321',
                             Site='www.testsite.com',
                             ParentID=paccount[0]['id']
                             )
        caccount = self.svc.create([caccount_data])
        self._todelete.append(caccount[0]['id'])

        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            AccountID=caccount[0]['id'],
                            Email='testfirstname@testlastname.com',
                            Birthdate=datetime.date(1965, 1, 5)
                            )
        contact = self.svc.create([contact_data])
        self._todelete.append(contact[0]['id'])

        query_res = self.svc.query(
            "Id, LastName, FirstName, Account.Site, Account.Parent.AccountNumber",
            "Contact",
            "Account.AccountNumber='987654321'",
        )

        rr = query_res.records[0]
        self.assertEqual(query_res.size, 1)
        self.assertEqual(rr.type, 'Contact')
        map(
            self.assertEqual,
            [
                rr.Id,
                rr.LastName,
                rr.FirstName,
                rr.Account.Site,
                rr.Account.Parent.AccountNumber,
            ],
            [
                contact[0]['id'],
                contact_data['LastName'],
                contact_data['FirstName'],
                caccount_data['Site'],
                paccount_data['AccountNumber'],
            ],
        )

    def testParentToChildMultiQuery(self):
        caccount_data = dict(type='Account',
                             Name='ChildTestAccount',
                             AccountNumber='987654321',
                             Site='www.testsite.com',
                             )
        caccount = self.svc.create([caccount_data])
        self._todelete.append(caccount[0]['id'])

        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            AccountID=caccount[0]['id'],
                            Email='testfirstname@testlastname.com',
                            Birthdate=datetime.date(1965, 1, 5)
                            )
        contact = self.svc.create([contact_data])
        self._todelete.append(contact[0]['id'])

        contact_data2 = dict(type='Contact',
                             LastName='TestLastName2',
                             FirstName='TestFirstName2',
                             Phone='123-456-7890',
                             AccountID=caccount[0]['id'],
                             Email='testfirstname2@testlastname2.com',
                             Birthdate=datetime.date(1965, 1, 5)
                             )
        contact2 = self.svc.create([contact_data2])
        self._todelete.append(contact2[0]['id'])

        query_res = self.svc.query(
            "Id, Name, (select FirstName from Contacts)",
            "Account",
            "AccountNumber='987654321'",
        )

        rr = query_res.records[0]
        self.assertEqual(query_res.size, 1)
        self.assertEqual(rr.type, 'Account')

        map(self.assertEqual,
            [rr.Id, rr.Name],
            [caccount[0]['id'], caccount_data['Name']])

    def testParentToChildMultiQuery2(self):
        caccount_data = dict(type='Account',
                             Name='ChildTestAccount',
                             AccountNumber='987654321',
                             Site='www.testsite.com',
                             )
        caccount = self.svc.create([caccount_data])
        self._todelete.append(caccount[0]['id'])

        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            AccountID=caccount[0]['id'],
                            Email='testfirstname@testlastname.com',
                            Birthdate=datetime.date(1965, 1, 5)
                            )
        contact = self.svc.create([contact_data])
        self._todelete.append(contact[0]['id'])

        contact_data2 = dict(type='Contact',
                             LastName='TestLastName2',
                             FirstName='TestFirstName2',
                             Phone='123-456-7890',
                             AccountID=caccount[0]['id'],
                             Email='testfirstname2@testlastname2.com',
                             Birthdate=datetime.date(1965, 1, 5)
                             )
        contact2 = self.svc.create([contact_data2])
        self._todelete.append(contact2[0]['id'])

        query_res = self.svc.query(
            "Id, Name, (select FirstName, Account.Site from Contacts), (select Name from Assets)",
            "Account",
            "AccountNumber='987654321'",
        )

        rr = query_res.records[0]
        self.assertEqual(query_res.size, 1)
        self.assertEqual(rr.type, 'Account')

        map(self.assertEqual,
            [rr.Id, rr.Name],
            [caccount[0]['id'], caccount_data['Name']])

        result = 0
        for name in [contact_data2['FirstName'],
                     contact_data['FirstName']]:
            if name in [rr.Contacts.records[i].FirstName for i in range(len(rr.Contacts.records))]:
                result += 1
        self.assertEqual(result, rr.Contacts.size)

    def testMultiQueryCount(self):
        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            Email='testfirstname@testlastname.com',
                            Birthdate=datetime.date(1965, 1, 5)
                            )
        contact = self.svc.create([contact_data])
        self._todelete.append(contact[0]['id'])

        contact_data2 = dict(type='Contact',
                             LastName='TestLastName2',
                             FirstName='TestFirstName2',
                             Phone='123-456-7890',
                             Email='testfirstname2@testlastname2.com',
                             Birthdate=datetime.date(1965, 1, 5)
                             )
        contact2 = self.svc.create([contact_data2])
        self._todelete.append(contact2[0]['id'])

        query_res = self.svc.query(
            "count()",
            "Contact",
            "Phone='123-456-7890'",
        )

        self.assertEqual(query_res.size, 2)

    def testAggregateQuery(self):
        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            Email='testfirstname@testlastname.com',
                            Birthdate=datetime.date(1900, 1, 5)
                            )
        contact = self.svc.create([contact_data])
        self._todelete.append(contact[0]['id'])

        res = self.svc.query("SELECT MAX(CreatedDate) FROM Contact GROUP BY LastName")
        # the aggregate result is in the 'expr0' attribute of the result
        self.assertTrue(hasattr(res[0], 'expr0'))
        # (unfortunately no field type info is returned as part of the
        # AggregateResult object, so we can't automatically marshall to the
        # correct Python type)

    def testQueryDoesNotExist(self):
        res = self.svc.query(
            'LastName, FirstName, Phone, Email, Birthdate',
            'Contact',
            "LastName = 'Doe'",
        )
        self.assertEqual(len(res), 0)

    def testQueryMore(self):
        self.svc.batchSize = 100
        data = list()
        for x in range(250):
            data.append(dict(type='Contact',
                             LastName='Doe',
                             FirstName='John',
                             Phone='123-456-7890',
                             Email='john@doe.com',
                             Birthdate=datetime.date(1970, 1, 4)
                             ))
        res = self.svc.create(data[:200])
        ids = [x['id'] for x in res]
        self._todelete.extend(ids)
        res = self.svc.create(data[200:])
        ids = [x['id'] for x in res]
        self._todelete.extend(ids)
        res = self.svc.query(
            'LastName, FirstName, Phone, Email, Birthdate',
            'Contact',
            "LastName = 'Doe'",
        )
        self.assertTrue(not res['done'])
        self.assertEqual(len(res), 200)
        res = self.svc.queryMore(res['queryLocator'])
        self.assertTrue(res['done'])
        self.assertEqual(len(res), 50)

    def testSearch(self):
        data = dict(type='Contact',
                    LastName='LongLastName',
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=datetime.date(1970, 1, 4)
                    )
        res = self.svc.create([data])
        self._todelete.append(res[0]['id'])

        # Requires some delay for indexing
        for attempt in range(DELAY_RETRY):
            sleep(DELAY_SEC)
            res = self.svc.search("FIND {Long} in ALL FIELDS RETURNING Contact(Id, Birthdate)")
            if len(res) > 0:
                break
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].type, 'Contact')
        self.assertEqual(type(res[0].Birthdate), datetime.date)
        res = self.svc.search("FIND {khgkshgsuhalsf} in ALL FIELDS RETURNING Contact(Id)")
        self.assertEqual(len(res), 0)

    def testGetDeleted(self):
        startdate = datetime.datetime.utcnow()
        enddate = startdate + datetime.timedelta(seconds=61)
        data = dict(type='Contact',
                    LastName='Doe',
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=datetime.date(1970, 1, 4)
                    )
        res = self.svc.create(data)
        id = res[0]['id']
        self.svc.delete(id)
        res = self.svc.getDeleted('Contact', startdate, enddate)
        self.assertTrue(len(res) != 0)
        ids = [r['id'] for r in res]
        self.assertTrue(id in ids)

    def testGetUpdated(self):
        startdate = datetime.datetime.utcnow()
        enddate = startdate + datetime.timedelta(seconds=61)
        data = dict(type='Contact',
                    LastName='Doe',
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=datetime.date(1970, 1, 4)
                    )
        res = self.svc.create(data)
        id = res[0]['id']
        self._todelete.append(id)
        data = dict(type='Contact',
                    Id=id,
                    FirstName='Jane')
        self.svc.update(data)
        res = self.svc.getUpdated('Contact', startdate, enddate)
        self.assertTrue(id in res)

    def testGetUserInfo(self):
        userinfo = self.svc.getUserInfo()
        self.assertTrue('accessibilityMode' in userinfo)
        self.assertTrue('currencySymbol' in userinfo)
        self.assertTrue('organizationId' in userinfo)
        self.assertTrue('organizationMultiCurrency' in userinfo)
        self.assertTrue('organizationName' in userinfo)
        self.assertTrue('userDefaultCurrencyIsoCode' in userinfo)
        self.assertTrue('userEmail' in userinfo)
        self.assertTrue('userFullName' in userinfo)
        self.assertTrue('userId' in userinfo)
        self.assertTrue('userLanguage' in userinfo)
        self.assertTrue('userLocale' in userinfo)
        self.assertTrue('userTimeZone' in userinfo)
        self.assertTrue('userUiSkin' in userinfo)

    def testDescribeTabs(self):
        tabinfo = self.svc.describeTabs()
        for info in tabinfo:
            self.assertTrue('label' in info)
            self.assertTrue('logoUrl' in info)
            self.assertTrue('selected' in info)
            self.assertTrue('tabs' in info)
            for tab in info['tabs']:
                self.assertTrue('custom' in tab)
                self.assertTrue('label' in tab)
                self.assertTrue('sObjectName' in tab)
                self.assertTrue('url' in tab)

    def testDescribeLayout(self):
        self.assertRaises(NotImplementedError, self.svc.describeLayout,
                          'Contact')

    def testSetMultiPicklistToEmpty(self):
        originalList = ["Pear", "Apple"]
        newList = []
        lastname = 'Doe'
        data = dict(type='Contact',
                    LastName=lastname,
                    FirstName='John',
                    Favorite_Fruit__c=originalList
                    )
        res = self.svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve(
            'LastName, Favorite_Fruit__c',
            'Contact',
            [id],
        )
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']), 2)
        data = dict(type='Contact',
                    Id=id,
                    Favorite_Fruit__c=newList)
        self.svc.update(data)
        contacts = self.svc.retrieve(
            'LastName, Favorite_Fruit__c',
            'Contact',
            [id],
        )
        self.assertTrue(isinstance(contacts[0]['Favorite_Fruit__c'], list))
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']), 0)

    def testAddToEmptyMultiPicklist(self):
        originalList = []
        newList = ["Pear", "Apple"]
        lastname = 'Doe'
        data = dict(type='Contact',
                    LastName=lastname,
                    FirstName='John',
                    Favorite_Fruit__c=originalList
                    )
        res = self.svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve(
            'LastName, Favorite_Fruit__c',
            'Contact',
            [id],
        )
        self.assertTrue(isinstance(contacts[0]['Favorite_Fruit__c'], list))
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']), 0)
        data = dict(type='Contact',
                    Id=id,
                    Favorite_Fruit__c=newList)
        self.svc.update(data)
        contacts = self.svc.retrieve(
            'LastName, Favorite_Fruit__c',
            'Contact',
            [id],
        )
        self.assertTrue(isinstance(contacts[0]['Favorite_Fruit__c'], list))
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']), 2)

    def testIsNillableField(self):
        res = self.svc.describeSObjects('Contact')
        self.assertFalse(res[0].fields['LastName'].nillable)
        self.assertTrue(res[0].fields['FirstName'].nillable)
        self.assertTrue(res[0].fields['Favorite_Fruit__c'].nillable)

    def testUpsert(self):
        data = dict(type='Contact',
                    LastName='Doe',
                    FirstName='John',
                    Phone='123-456-7890',
                    Email='john@doe.com',
                    Birthdate=datetime.date(1970, 1, 4)
                    )
        res = self.svc.upsert('Email', [data])
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

    def testPrepareSObjectsWithNone(self):
        obj = {
            'val': None,
        }
        prepped_obj = _prepareSObjects([obj])
        self.assertEqual(prepped_obj,
                         [{'val': [],
                           'fieldsToNull': ['val'],
                           }])

    def testRetrieveTextWithNewlines(self):
        data = dict(type='Contact',
                    LastName='Doe',
                    FirstName='John',
                    Description='This is a\nmultiline description.',
                    )
        res = self.svc.create([data])
        self.assertTrue(type(res) in (list, tuple))
        self.assertTrue(len(res) == 1)
        self.assertTrue(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve('FirstName, Description', 'Contact', [id])
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        self.assertEqual(data['FirstName'], contact['FirstName'])
        self.assertEqual(data['Description'], contact['Description'])

    @unittest.skip("Email is not working...")
    def testSendSimpleEmail(self):
        testemail = {
            'subject': 'pyforce test_xmlclient.py testSendSimpleEmail of Salesforce sendEmail()',
            'saveAsActivity': False,
            'toAddresses': str(self.svc.getUserInfo()['userEmail']),
            'plainTextBody': 'This is a test email message with HTML markup.\n\nYou are currently looking at the plain-text body, but the message is sent in both forms.',
        }
        res = self.svc.sendEmail([testemail])
        print(res)
        self.assertTrue(res[0]['success'])

    @unittest.skip("Email is not working...")
    def testSendEmailMissingFields(self):
        testemail = {
            'toAddresses': str(self.svc.getUserInfo()['userEmail']),
        }
        res = self.svc.sendEmail([testemail])
        self.assertFalse(res[0]['success'])
        self.assertEqual(res[0]['errors'][0]['statusCode'], 'REQUIRED_FIELD_MISSING')

    @unittest.skip("Email is not working...")
    def testSendHTMLEmailWithAttachment(self):
        solid_logo = {
            'body': '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',
            'contentType': 'image/png',
            'fileName': 'salesforce_logo.png',
            'inline': True
        }
        testemail = {
            'subject': 'pyforce test_xmlclient.py testSendHTMLEmailWithAttachment of Salesforce sendEmail()',
            'useSignature': True,
            'saveAsActivity': False,
            'toAddresses': str(self.svc.getUserInfo()['userEmail']),
            'plainTextBody': 'This is a test email message with HTML markup.\n\nYou are currently looking at the plain-text body, but the message is sent in both forms.',
            'htmlBody': '<html><head><meta http-equiv="content-type" content="text/html; charset=utf-8"><body><h1>This is a test email message with HTML markup.</h1>\n\n<p>You are currently looking at the <i>HTML</i> body, but the message is sent in both forms.</p></body></html>',
            'inReplyTo': '<1234567890123456789%example@example.com>',
            'references': '<1234567890123456789%example@example.com>',
            'fileAttachments': [solid_logo]
        }
        res = self.svc.sendEmail([testemail])
        self.assertTrue(res[0]['success'])

    def testLogout(self):
        """Logout and verify that the previous sessionId longer works."""
        result = self.svc.getUserInfo()
        self.assertIn('userId', result)
        response = self.svc.logout()
        self.assertTrue(response, "Logout didn't return _tPartnerNS.logoutResponse")
        with self.assertRaises(pyforce.SessionTimeoutError) as cm:
            # Sometimes this doesn't work on the first try. Flakey...
            for _ in range(DELAY_RETRY):
                sleep(DELAY_SEC)
                result = self.svc.getUserInfo()
        self.assertEqual(cm.exception.faultCode, 'INVALID_SESSION_ID', "Session didn't fail with INVALID_SESSION_ID.")


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtils),
    ))


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
