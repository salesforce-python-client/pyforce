from types import DictType, StringTypes, IntType, ListType, TupleType
import unittest
import datetime

import sfconfig
import pyforce

from pyforce import SoapFaultError
from pyforce.pyforce import _prepareSObjects

class TestUtils(unittest.TestCase):

    def setUp(self):
        self.svc = svc = pyforce.PythonClient()
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
    
    def testDescribeGlobal(self):
        svc = self.svc
        res = svc.describeGlobal()
        self.assertEqual(type(res), DictType)
        self.failUnless(type(res['encoding']) in StringTypes)
        self.assertEqual(type(res['maxBatchSize']), IntType)
        self.assertEqual(type(res['types']), ListType)
        self.failUnless(len(res['sobjects']) > 0)
        # BBB for API < 17.0
        self.failUnless(len(res['types']) > 0)
    
    def testDescribeSObjects(self):
        svc = self.svc
        globalres = svc.describeGlobal()
        types = globalres['types'][:100]
        res = svc.describeSObjects(types[0])
        self.assertEqual(type(res), ListType)
        self.assertEqual(len(res), 1)
        res = svc.describeSObjects(types)
        self.assertEqual(len(types), len(res))
    
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
                
    
    def testSetIntegerField(self):
    #Passes when you feed it floats, even if salesforce field is defined for 0 decimal places.  Lack of data validation in SF?
        svc = self.svc
        testField = 'Favorite_Integer__c'
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Favorite_Integer__c = -25
            )
        res = svc.create([data])
        self.failUnless(type(res) in (ListType, TupleType))
        self.failUnless(len(res) == 1)
        self.failUnless(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, FirstName, Favorite_Integer__c', 'Contact', [id])
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        self.assertEqual(data[testField], contact[testField])
    
    def testSetFloatField(self):
    # this fails when you have a large amount (I didn't test the #) of decimal places.
        svc = self.svc
        testField = 'Favorite_Float__c'
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Favorite_Float__c = -1.999888777
            )
        res = svc.create([data])
        self.failUnless(type(res) in (ListType, TupleType))
        self.failUnless(len(res) == 1)
        self.failUnless(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, FirstName, Favorite_Float__c', 'Contact', [id])
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        self.assertEqual(data[testField], contact[testField])
    
    def testCreatePickListMultiple(self):
         svc = self.svc
        
         data = dict(type='Contact',
             LastName='Doe',
             FirstName='John',
             Phone='123-456-7890',
             Email='john@doe.com',
             Birthdate = datetime.date(1970, 1, 4),
             Favorite_Fruit__c = ["Apple","Orange","Pear"]
             )
         res = svc.create([data])
         self.failUnless(type(res) in (ListType, TupleType))
         self.failUnless(len(res) == 1)
         self.failUnless(res[0]['success'])
         id = res[0]['id']
         self._todelete.append(id)
         contacts = svc.retrieve('LastName, FirstName, Phone, Email, Birthdate, \
             Favorite_Fruit__c', 'Contact', [id])
         self.assertEqual(len(contacts), 1)
         contact = contacts[0]
         for k in ['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate', 'Favorite_Fruit__c']:
             self.assertEqual(
                 data[k], contact[k])
    
     #def testCreatePickListMultipleWithInvalid(self):
         #""" This fails, and I guess it should(?) 
         #     SF doesn't enforce vocabularies, appearently """
         #svc = self.svc
        
         #data = dict(type='Contact',
             #LastName='Doe',
             #FirstName='John',
             #Phone='123-456-7890',
             #Email='john@doe.com',
             #Birthdate = datetime.date(1970, 1, 4),
             #Favorite_Fruit__c = ["Apple","Orange","Pear","RottenFruit"]
             #)
         #res = svc.create([data])
         #self.failUnless(type(res) in (ListType, TupleType))
         #self.failUnless(len(res) == 1)
         #self.failUnless(res[0]['success'])
         #id = res[0]['id']
         #self._todelete.append(id)
         #contacts = svc.retrieve('LastName, FirstName, Phone, Email, Birthdate, \
             #Favorite_Fruit__c', 'Contact', [id])
         #self.assertEqual(len(contacts), 1)
         #contact = contacts[0]
         #self.assertNotEqual(data['Favorite_Fruit__c'], contact['Favorite_Fruit__c'])
         #self.assertEqual(len(contact['Favorite_Fruit__c']),3)
         #for k in ['LastName', 'FirstName', 'Phone', 'Email', 'Birthdate', 'Favorite_Fruit__c']:
             #self.assertEqual(
                 #data[k], contact[k])            
    
    def testFailedCreate(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = 'foo'
            )
        self.assertRaises(SoapFaultError, svc.create, data)
    
    def testRetrieve(self):
        svc = self.svc
        data = dict(type='Contact',
             LastName='Doe',
             FirstName='John',
             Phone='123-456-7890',
             Email='john@doe.com',
             Birthdate = datetime.date(1970, 1, 4)
             )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        typedesc = svc.describeSObjects('Contact')[0]
        fieldnames = list()
        fields = typedesc.fields.values()
        fieldnames = [f.name for f in fields]
        fieldnames = ', '.join(fieldnames)
        contacts = svc.retrieve(fieldnames, 'Contact', [id])
        self.assertEqual(len(contacts), 1)
    
    def testRetrieveDeleted(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create(data)
        id = res[0]['id']
        svc.delete(id)
        typedesc = svc.describeSObjects('Contact')[0]
        fieldnames = list()
        fields = typedesc.fields.values()
        fieldnames = [f.name for f in fields]
        fieldnames = ', '.join(fieldnames)
        contacts = svc.retrieve(fieldnames, 'Contact', [id])
        self.assertEqual(len(contacts), 0)
    
    def testDelete(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.create([data])
        id = res[0]['id']
        res = svc.delete([id])
        self.failUnless(res[0]['success'])
        contacts = svc.retrieve('LastName', 'Contact', [id])
        self.assertEqual(len(contacts), 0)
    
    def testUpdate(self):
        svc = self.svc
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
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, Birthdate', 'Contact', [id])
        self.assertEqual(contacts[0]['Birthdate'], originaldate)
        self.assertEqual(contacts[0]['LastName'], lastname)
        data = dict(type='Contact',
            Id=id,
            Birthdate = newdate)
        svc.update(data)
        contacts = svc.retrieve('LastName, Birthdate', 'Contact', [id])
        self.assertEqual(contacts[0]['Birthdate'], newdate)
        self.assertEqual(contacts[0]['LastName'], lastname)
    
    def testShrinkMultiPicklist(self):
        svc = self.svc
        originalList = ["Pear","Apple"]
        newList = ["Pear",]
        lastname = 'Doe'
        data = dict(type='Contact',
            LastName=lastname,
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Favorite_Fruit__c=originalList
            )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),2)
        data = dict(type='Contact',
            Id=id,
            Favorite_Fruit__c=newList)
        svc.update(data)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),1)
    
    def testGrowMultiPicklist(self):
        svc = self.svc
        originalList = ["Pear","Apple"]
        newList = ["Pear", "Apple", "Orange"]
        lastname = 'Doe'
        data = dict(type='Contact',
            LastName=lastname,
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Favorite_Fruit__c=originalList
            )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),2)
        data = dict(type='Contact',
            Id=id,
            Favorite_Fruit__c=newList)
        svc.update(data)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),3)
    
    def testUpdateDeleted(self):
        svc = self.svc
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
        res = svc.create(data)
        id = res[0]['id']
        svc.delete(id)
        contacts = svc.retrieve('LastName, Birthdate', 'Contact', [id])
        self.assertEqual(len(contacts), 0)
        data = dict(type='Contact',
            Id=id,
            Birthdate = newdate)
        res = svc.update(data)
        self.failUnless(not res[0]['success'])
        self.failUnless(len(res[0]['errors']) > 0)
    
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
        res = svc.query("SELECT LastName, FirstName, Phone, Email, Birthdate FROM Contact WHERE LastName = 'Doe'")
        self.assertEqual(res['size'], 2)
        res = svc.query("SELECT Id, LastName, FirstName, Phone, Email, Birthdate FROM Contact WHERE LastName = 'Doe' and FirstName = 'Jane'")
        self.assertEqual(res['size'], 1)
        self.assertEqual(res['records'][0]['Id'], janeid)
    
    def testBackwardsCompatibleQuery(self):
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
        # conditional expression as positional arg
        res = svc.query('LastName, FirstName, Phone, Email, Birthdate',
                'Contact', "LastName = 'Doe'")
        self.assertEqual(res['size'], 2)
        # conditional expression as *empty* positional arg
        res = svc.query('LastName', 'Contact', '')
        self.failUnless(res['size'] > 0)
        # conditional expression as kwarg
        res = svc.query('Id, LastName, FirstName, Phone, Email, Birthdate',
                'Contact', conditionalExpression="LastName = 'Doe' and FirstName = 'Jane'")
        self.assertEqual(res['size'], 1)
        self.assertEqual(res['records'][0]['Id'], janeid)
    
    def testTypeDescriptionsCache(self):
        # patch describeSObjects to make a record when it is called
        calls = []
        standard_describeSObjects = pyforce.PythonClient.describeSObjects
        def patched_describeSObjects(self, sObjectTypes):
            calls.append(sObjectTypes)
            return standard_describeSObjects(self, sObjectTypes)
        pyforce.PythonClient.describeSObjects = patched_describeSObjects
        
        # turn the cache on
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
        svc = self.svc
        account_data = dict(type='Account',
                            Name='ChildTestAccount',
                            AccountNumber='987654321',
                            Site='www.testsite.com',
                           )
        account = svc.create([account_data])
        self._todelete.append(account[0]['id'])
    
        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            AccountID=account[0]['id'],
                            Email='testfirstname@testlastname.com',
                            Birthdate = datetime.date(1965, 1, 5)
                           )
        contact = svc.create([contact_data])
        self._todelete.append(contact[0]['id'])
    
        query_res = svc.query("Id, LastName, FirstName, Account.Site, Account.AccountNumber",
                              "Contact",
                              "Phone='123-456-7890'"
                             )
        
        self.assertEqual(query_res.size, 1)
        rr = query_res.records[0]
        self.assertEqual(rr.type, 'Contact')
        map(self.assertEqual,
            [rr.Id, rr.LastName, rr.FirstName, rr.Account.Site, rr.Account.AccountNumber],
            [contact[0]['id'], contact_data['LastName'], contact_data['FirstName'], account_data['Site'], account_data['AccountNumber']])
    
    def testChildToParentMultiQuery2(self):
        svc = self.svc
        paccount_data = dict(type='Account',
                             Name='ParentTestAccount',
                             AccountNumber='123456789',
                             Site='www.testsite.com',
                            )
        paccount = svc.create([paccount_data])
        self._todelete.append(paccount[0]['id'])
    
        caccount_data= dict(type='Account',
                            Name='ChildTestAccount',
                            AccountNumber='987654321',
                            Site='www.testsite.com',
                            ParentID=paccount[0]['id']
                           )
        caccount = svc.create([caccount_data])
        self._todelete.append(caccount[0]['id'])
    
        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            AccountID=caccount[0]['id'],
                            Email='testfirstname@testlastname.com',
                            Birthdate = datetime.date(1965, 1, 5)
                           )
        contact = svc.create([contact_data])
        self._todelete.append(contact[0]['id'])
    
        query_res = svc.query("Id, LastName, FirstName, Account.Site, Account.Parent.AccountNumber",
                              "Contact",
                              "Account.AccountNumber='987654321'"
                             )
    
        rr = query_res.records[0]
        self.assertEqual(query_res.size, 1)
        self.assertEqual(rr.type, 'Contact')
        map(self.assertEqual,
            [rr.Id, rr.LastName, rr.FirstName, rr.Account.Site, rr.Account.Parent.AccountNumber],
            [contact[0]['id'], contact_data['LastName'], contact_data['FirstName'], caccount_data['Site'], paccount_data['AccountNumber']])
    
    def testParentToChildMultiQuery(self):
        svc = self.svc
        caccount_data= dict(type='Account',
                            Name='ChildTestAccount',
                            AccountNumber='987654321',
                            Site='www.testsite.com',
                           )
        caccount = svc.create([caccount_data])
        self._todelete.append(caccount[0]['id'])
    
        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            AccountID=caccount[0]['id'],
                            Email='testfirstname@testlastname.com',
                            Birthdate = datetime.date(1965, 1, 5)
                           )
        contact = svc.create([contact_data])
        self._todelete.append(contact[0]['id'])
    
        contact_data2 = dict(type='Contact',
                            LastName='TestLastName2',
                            FirstName='TestFirstName2',
                            Phone='123-456-7890',
                            AccountID=caccount[0]['id'],
                            Email='testfirstname2@testlastname2.com',
                            Birthdate = datetime.date(1965, 1, 5)
                           )
        contact2 = svc.create([contact_data2])
        self._todelete.append(contact2[0]['id'])
    
        query_res = svc.query("Id, Name, (select FirstName from Contacts)",
                              "Account",
                              "AccountNumber='987654321'"
                             )
    
        rr = query_res.records[0]
        self.assertEqual(query_res.size, 1)
        self.assertEqual(rr.type, 'Account')
    
        map(self.assertEqual,
            [rr.Id, rr.Name],
            [caccount[0]['id'], caccount_data['Name']])
    
    def testParentToChildMultiQuery2(self):
        svc = self.svc
        caccount_data= dict(type='Account',
                            Name='ChildTestAccount',
                            AccountNumber='987654321',
                            Site='www.testsite.com',
                           )
        caccount = svc.create([caccount_data])
        self._todelete.append(caccount[0]['id'])
    
        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            AccountID=caccount[0]['id'],
                            Email='testfirstname@testlastname.com',
                            Birthdate = datetime.date(1965, 1, 5)
                           )
        contact = svc.create([contact_data])
        self._todelete.append(contact[0]['id'])
    
        contact_data2 = dict(type='Contact',
                            LastName='TestLastName2',
                            FirstName='TestFirstName2',
                            Phone='123-456-7890',
                            AccountID=caccount[0]['id'],
                            Email='testfirstname2@testlastname2.com',
                            Birthdate = datetime.date(1965, 1, 5)
                           )
        contact2 = svc.create([contact_data2])
        self._todelete.append(contact2[0]['id'])
    
        query_res = svc.query("Id, Name, (select FirstName, Account.Site from Contacts), (select Name from Assets)",
                              "Account",
                              "AccountNumber='987654321'"
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
        svc = self.svc
        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            Email='testfirstname@testlastname.com',
                            Birthdate = datetime.date(1965, 1, 5)
                           )
        contact = svc.create([contact_data])
        self._todelete.append(contact[0]['id'])
    
        contact_data2 = dict(type='Contact',
                           LastName='TestLastName2',
                            FirstName='TestFirstName2',
                            Phone='123-456-7890',
                            Email='testfirstname2@testlastname2.com',
                            Birthdate = datetime.date(1965, 1, 5)
                           )
        contact2 = svc.create([contact_data2])
        self._todelete.append(contact2[0]['id'])
    
        query_res = svc.query("count()",
                              "Contact",
                              "Phone='123-456-7890'"
                             )
    
        self.assertEqual(query_res.size, 2)
    
    def testAggregateQuery(self):
        svc = self.svc
        contact_data = dict(type='Contact',
                            LastName='TestLastName',
                            FirstName='TestFirstName',
                            Phone='123-456-7890',
                            Email='testfirstname@testlastname.com',
                            Birthdate = datetime.date(1900, 1, 5)
                           )
        contact = svc.create([contact_data])
        self._todelete.append(contact[0]['id'])
        
        res = svc.query("SELECT MAX(CreatedDate) FROM Contact GROUP BY LastName")
        # the aggregate result is in the 'expr0' attribute of the result
        self.failUnless(hasattr(res[0], 'expr0'))
        # (unfortunately no field type info is returned as part of the
        # AggregateResult object, so we can't automatically marshall to the
        # correct Python type)
    
    def testQueryDoesNotExist(self):
        res = self.svc.query('LastName, FirstName, Phone, Email, Birthdate',
                'Contact', "LastName = 'Doe'")
        self.assertEqual(res['size'], 0)
    
    def testQueryMore(self):
        svc = self.svc
        svc.batchSize = 100
        data = list()
        for x in range(250):
            data.append(dict(type='Contact',
                LastName='Doe',
                FirstName='John',
                Phone='123-456-7890',
                Email='john@doe.com',
                Birthdate = datetime.date(1970, 1, 4)
                ))
        res = svc.create(data[:200])
        ids = [x['id'] for x in res]
        self._todelete.extend(ids)
        res = svc.create(data[200:])
        ids = [x['id'] for x in res]
        self._todelete.extend(ids)
        res = svc.query('LastName, FirstName, Phone, Email, Birthdate',
                'Contact', "LastName = 'Doe'")
        self.failUnless(not res['done'])
        self.assertEqual(len(res['records']), 200)
        res = svc.queryMore(res['queryLocator'])
        self.failUnless(res['done'])
        self.assertEqual(len(res['records']), 50)
    
    def testSearch(self):
        res = self.svc.search("FIND {barr} in ALL FIELDS RETURNING Contact(Id, Birthdate)")
        self.assertEqual(len(res), 1)
        self.assertEqual(res[0].type, 'Contact')
        self.assertEqual(type(res[0].Birthdate), datetime.date)
        
        res = self.svc.search("FIND {khgkshgsuhalsf} in ALL FIELDS RETURNING Contact(Id)")
        self.assertEqual(len(res), 0)
    
    def testGetDeleted(self):
        svc = self.svc
        startdate = datetime.datetime.utcnow()
        enddate = startdate + datetime.timedelta(seconds=61)
        data = dict(type='Contact',
                LastName='Doe',
                FirstName='John',
                Phone='123-456-7890',
                Email='john@doe.com',
                Birthdate = datetime.date(1970, 1, 4)
                )
        res = svc.create(data)
        id = res[0]['id']
        svc.delete(id)
        res = svc.getDeleted('Contact', startdate, enddate)
        self.failUnless(len(res) != 0)
        ids = [r['id'] for r in res]
        self.failUnless(id in ids)
    
    def testGetUpdated(self):
        svc = self.svc
        startdate = datetime.datetime.utcnow()
        enddate = startdate + datetime.timedelta(seconds=61)
        data = dict(type='Contact',
                LastName='Doe',
                FirstName='John',
                Phone='123-456-7890',
                Email='john@doe.com',
                Birthdate = datetime.date(1970, 1, 4)
                )
        res = svc.create(data)
        id = res[0]['id']
        self._todelete.append(id)
        data = dict(type='Contact',
                Id=id,
                FirstName='Jane')
        svc.update(data)
        res = svc.getUpdated('Contact', startdate, enddate)
        self.failUnless(id in res)
    
    def testGetUserInfo(self):
        svc = self.svc
        userinfo = svc.getUserInfo()
        self.failUnless('accessibilityMode' in userinfo)
        self.failUnless('currencySymbol' in userinfo)
        self.failUnless('organizationId' in userinfo)
        self.failUnless('organizationMultiCurrency' in userinfo)
        self.failUnless('organizationName' in userinfo)
        self.failUnless('userDefaultCurrencyIsoCode' in userinfo)
        self.failUnless('userEmail' in userinfo)
        self.failUnless('userFullName' in userinfo)
        self.failUnless('userId' in userinfo)
        self.failUnless('userLanguage' in userinfo)
        self.failUnless('userLocale' in userinfo)
        self.failUnless('userTimeZone' in userinfo)
        self.failUnless('userUiSkin' in userinfo)
    
    def testDescribeTabs(self):
        tabinfo = self.svc.describeTabs()
        for info in tabinfo:
            self.failUnless('label' in info)
            self.failUnless('logoUrl' in info)
            self.failUnless('selected' in info)
            self.failUnless('tabs' in info)
            for tab in info['tabs']:
                self.failUnless('custom' in tab)
                self.failUnless('label' in tab)
                self.failUnless('sObjectName' in tab)
                self.failUnless('url' in tab)
    
    def testDescribeLayout(self):
        svc = self.svc
        self.assertRaises(NotImplementedError, svc.describeLayout,
            'Contact')
    
    def testSetMultiPicklistToEmpty(self):
        svc = self.svc
        originalList = ["Pear","Apple"]
        newList = []
        lastname = 'Doe'
        data = dict(type='Contact',
            LastName=lastname,
            FirstName='John',
            Favorite_Fruit__c=originalList
            )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),2)
        data = dict(type='Contact',
            Id=id,
            Favorite_Fruit__c=newList)
        svc.update(data)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.failUnless(isinstance(contacts[0]['Favorite_Fruit__c'], list))
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),0)  
    
    def testAddToEmptyMultiPicklist(self):
        svc = self.svc
        originalList = []
        newList = ["Pear","Apple"]
        lastname = 'Doe'
        data = dict(type='Contact',
            LastName=lastname,
            FirstName='John',
            Favorite_Fruit__c=originalList
            )
        res = svc.create([data])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.failUnless(isinstance(contacts[0]['Favorite_Fruit__c'], list))
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),0)
        data = dict(type='Contact',
            Id=id,
            Favorite_Fruit__c=newList)
        svc.update(data)
        contacts = svc.retrieve('LastName, Favorite_Fruit__c', 'Contact', [id])
        self.failUnless(isinstance(contacts[0]['Favorite_Fruit__c'], list))
        self.assertEqual(len(contacts[0]['Favorite_Fruit__c']),2)  
    
    def testIsNillableField(self):
        svc = self.svc
        res = svc.describeSObjects('Contact')
        self.assertFalse(res[0].fields['LastName'].nillable)
        self.assertTrue(res[0].fields['FirstName'].nillable)
        self.assertTrue(res[0].fields['Favorite_Fruit__c'].nillable)
    
    def testUpsert(self):
        svc = self.svc
        data = dict(type='Contact',
            LastName='Doe',
            FirstName='John',
            Phone='123-456-7890',
            Email='john@doe.com',
            Birthdate = datetime.date(1970, 1, 4)
            )
        res = svc.upsert('Email', [data])
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
            Description="This is a\nmultiline description.",
            )
        res = self.svc.create([data])
        self.failUnless(type(res) in (ListType, TupleType))
        self.failUnless(len(res) == 1)
        self.failUnless(res[0]['success'])
        id = res[0]['id']
        self._todelete.append(id)
        contacts = self.svc.retrieve('Description', 'Contact', [id])
        self.assertEqual(len(contacts), 1)
        contact = contacts[0]
        self.assertEqual(data['Description'], contact['Description'])

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(TestUtils),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
