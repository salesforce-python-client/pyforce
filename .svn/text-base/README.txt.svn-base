Introduction
============

This is a distutils-packaged and updated version of the `beatbox module`_
by Simon Fell, which is a Python implementation of a client for the
Salesforce.com Partner Web Services API.

.. _`beatbox module`: http://www.pocketsoap.com/beatbox/

This module contains 2 versions of the Salesforce.com client:

 XMLClient
   The original beatbox version of the client which returns xmltramp objects.
 PythonClient
   Marshalls the returned objects into proper Python data types. e.g. integer
   fields return integers.


Compatibility
=============

Beatbox supports versions 16.0 through 20.0 of the Salesforce Partner Web
Services API. However, the following API calls have not been implemented at
this time:

 * convertLead
 * emptyRecycleBin
 * invalidateSessions
 * logout
 * merge
 * process
 * queryAll
 * undelete
 * describeSObject
 * sendEmail
 * describeDataCategoryGroups
 * describeDataCategoryGroupStructures

Beatbox has been tested with Python 2.4 and Python 2.6.


Basic Usage Examples
====================

Instantiate a Python Salesforce.com client:
  >>> svc = beatbox.PythonClient()
  >>> svc.login('username', 'passwordTOKEN')
  
(Note that interacting with Salesforce.com via the API requires the use of a
'security token' which must be appended to the password.)

Query for contacts with last name 'Doe':
  >>> res = svc.query("SELECT Id, FirstName, LastName FROM Contact WHERE LastName='Doe'")
  >>> res[0]
  {'LastName': 'Doe', 'type': 'Contact', 'Id': '0037000000eRf6vAAC', 'FirstName': 'John'}
  >>> res[0].Id
  '0037000000eRf6vAAC'

Add a new Lead:
  >>> contact = {'type': 'Lead', 'LastName': 'Glick', 'FirstName': 'David', 'Company': 'Individual'}
  >>> res = svc.create(contact)
Get the ID of the newly created Lead:
  >>> res[0]['id']
  '00Q7000000RVyiHEAT'


More Examples
=============

The examples folder contains the examples for the original beatbox. For
examples on how to use the PythonClient see
src/beatbox/tests/test_pythonClient.py.

Some of these other products that have been built on top of beatbox can also
provide example of use:
  
  * `Salesforce Base Connector`_
  * `Salesforce PFG Adapter`_
  * `Salesforce Auth Plugin`_
  * `RSVP for Salesforce`_

.. _`Salesforce Base Connector`: http://plone.org/products/salesforcebaseconnector
.. _`Salesforce PFG Adapter`: http://plone.org/products/salesforcepfgadapter
.. _`Salesforce Auth Plugin`: http://plone.org/products/salesforceauthplugin
.. _`RSVP for Salesforce`: http://plone.org/products/collective.salesforce.rsvp


Alternatives
============

David Lanstein has created a `Python Salesforce Toolkit`_ that is based on the
`suds`_ SOAP library.  Based on limited tests it appears to be somewhat slower
than beatbox for operations that return a lot of data; however, it may be a
better option if you want to be able to automatically generate a service proxy
for a new WSDL (such as for the Enterprise web services API).

.. _`Python Salesforce Toolkit`: http://code.google.com/p/salesforce-python-toolkit/
.. _`suds`: https://fedorahosted.org/suds/

Ron Hess from Salesforce.com has adapted beatbox for use with Google App
Engine.  See http://code.google.com/p/force-app-engine/


Running Tests
=============

First, we need to add some custom fields to the Contacts object in your Salesforce instance:

 * Login to your Salesforce.com instance
 * Browse to Setup --> Customize --> Contacts --> Fields --> "New" button
 * Add a Picklist (multi-select) labeled "Favorite Fruit", then add
    * Apple
    * Orange
    * Pear
 * Leave default of 3 lines and field name should default to "Favorite_Fruit"
 * Add a Number labeled "Favorite Integer", with 18 places, 0 decimal places
 * Add a Number labeled "Favorite Float", with 13 places, 5 decimal places

Create a sfconfig file in your python path with the following format::

    USERNAME='your salesforce username'
    PASSWORD='your salesforce passwordTOKEN'

where TOKEN is your Salesforce API login token.

Add './src' to your PYTHONPATH

Run the tests::

    python src/beatbox/tests/test_beatbox.py
    python src/beatbox/tests/test_pythonClient.py

