Running Installies
==================

Prerequisites
-------------

Setting up the Database
***********************

Installies uses MySQL as it's database, so you will need to install that first. You will also need
to create a database for installies.

Creating the Config File
************************

You will need to create a configuration file in ``/etc/installies`` named ``config.ini`` before
you can run Installies. Here is an example configuration:

.. code-block:: ini

   [server]
   Host = 0.0.0.0
   Port = 8000
   Protocol = http
   DebugMode = yes

   [database]
   Name = Installies
   User = installies
   Passwd = password
   Host = localhost
   Port = 3306

   [script]
   UploadPath = /path/where/to/put/apps/and/scripts
   MaxLength = 10000

   [email]
   Enabled = no
   User = installies@yourdomain.tld
   Passwd = pass123
   SMTPAddr = mail.example.com
   SMTPPort = 465
       
Installing
----------

Since installies is a python package, you can install Installies with pip. This will
install all dependancies.

.. code-block:: bash

   pip install .


Creating the Database Tables
****************************

Before running Installies, you will need to create the database tables. to do this you can open
your python interpreter and run the following code.

.. code-block:: python
   
   >>> from installies.database.database import create_database
   >>> create_database()
  

Running
-------

You can run Installies with python3.

.. code-block:: bash

   python3 -m installies
