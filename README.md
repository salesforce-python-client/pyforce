Introduction
============

This is a reluctant fork of the beatbox project originally authored by Simon 
Fell, (his version locked at 0.92) later drastically changed by these guys
https://code.google.com/p/salesforce-beatbox/ (versioned at 20.0).

Renamed to `pyforce` to avoid confusion related to the fractured community
version. (https://github.com/superfell/Beatbox/issues/6) Long story short,
the python client in the fork at version 20.0 is exceptionally useful, so
going back to 0.92 would be a mistake, however the beatbox version at 20.0 is
also no longer maintained (judging by the issues).  `pyforce` builds off of
the version available there, integrating bug fixes, and new features.

This module contains 2 versions of the Salesforce.com client:

 XMLClient
    An xmltramp wrapper that handles the xml fun.
 PythonClient
   Marshalls the returned objects into proper Python data types. e.g. integer
   fields return integers.

Compatibility
=============

`pyforce` supports versions 16.0 through 20.0 of the Salesforce Partner Web
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

`pyforce` supports python 2.x for values of x >=6.  It probably works in 2.4,
but not officially supported.

Basic Usage Examples
====================

Instantiate a Python Salesforce.com client:
    >>> svc = pyforce.Client()
    >>> svc.login('username', 'passwordTOKEN')

(Note that interacting with Salesforce.com via the API requires the use of a
'security token' which must be appended to the password.  See sfdc docs for
details)

The pyforce client allows you to query with sfdc SOQL.

Here's an example of a query for contacts with last name 'Doe':
    >>> res = svc.query("SELECT Id, FirstName, LastName FROM Contact WHERE LastName='Doe'")
    >>> res[0]
    {'LastName': 'Doe', 'type': 'Contact', 'Id': '0037000000eRf6vAAC', 'FirstName': 'John'}
    >>> res[0].Id
    '0037000000eRf6vAAC'

Add a new Lead:
    contact = {
            'type': 'Lead', 
            'LastName': 'Ian', 
            'FirstName': 'Bentley', 
            'Company': '10gen'
        }
    res = svc.create(contact)
    if not res[0]['errors']:
        contact_id = res[0]['id']
    else:
        raise Exception('Contact creation failed {0}'.format(res[0]['errors']))

Batches work automatically (though sfdc limits the number to 200 maximum):
    contacts = [
        {
            'type': 'Lead', 
            'LastName': 'Glick', 
            'FirstName': 'David', 
            'Company': 'Individual'
        },
        {
            'type': 'Lead', 
            'LastName': 'Ian', 
            'FirstName': 'Bentley', 
            'Company': '10gen'
        }
    ]
    res = svc.create(contacts)

More Examples
=============

The examples folder contains the examples for the xml client. For examples on 
how to use the python client see the tests directory.

Some of these other products that were built on top of beatbox can also provide
example of `pyforce` use, though this project may diverge from the beatbox api.

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

David Lanstein has created a `Python Salesforce Toolkit` that is based on the
`suds` SOAP library.  That project has not seen any commit since June 2011, so
it is assumed to be abandoned.

.. `Python Salesforce Toolkit`: http://code.google.com/p/salesforce-python-toolkit/

Running Tests
=============

At the fork time, all tests are integration tests that require access to a
Salesforce environment.  It is my intent to change these tests to be stub
based unit tests.

From the beatbox documentation:

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

    python src/pyforce/tests/test_xmlclient.py
    python src/pyforce/tests/test_pythonClient.py

