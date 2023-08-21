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

You will need to put a .env file in the ``src/installies`` directory. This file need to include
a few variables.

.. list-table::

   * - **Name**
     - **Description**
   * - DATABASE_NAME
     - The name of the database you have created for Installies;
   * - DATABASE_USER
     - The username of the user to access the database.
   * - DATABASE_PASS
     - The password of the user.
   * - DATABASE_HOST
     - The host of the mysql server.
   * - DATABASE_PORT
     - The port of the mysql server.
   * - SCRIPT_UPLOAD_PATH
     - The directory to store the scripts uploaded.
   * - NOREPLY_EMAIL
     - The email for account verification.
   * - NOREPLY_EMAIL_PASSWORD
     - The password/key for the email.
   * - SMTP_SERVER
     - The server address for the email server to use.
   * - SMTP_SERVER_PORT
     - The port of the email server.
       
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

You can run Installies in python3.

.. code-block:: bash

   python3 -m installies
