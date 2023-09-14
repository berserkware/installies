How to use the CLI
==================

The CLI makes it easy to install apps by finding scripts that work on your distros. The CLI also allows for
automatic caching of scripts.

Installing the CLI
------------------

You can install the CLI through the `Installies app <https://installies.org/apps/installies>`_ on Installies. You will
need python and pip installed for the install script and CLI to work.

.. code-block::

   $ chmod +x ./installies.sh
   $ ./installies.sh install

Common Actions
--------------

Installing
**********

.. code-block::

   $ installies install app_name

If the app is already installed, it will warn and ask you if you want to proceed with executing the script.

Removing
********

.. code-block::

   $ installies remove app_name

If the app isn't installed, it will warn and ask you if you want to proceed with executing the script.

Updating
********

.. code-block::

   $ installies update app_name

If the app isn't installed, it will warn and ask you if you want to proceed with executing the script.

Compiling
*********

.. code-block::

   $ installies compile app_name

If the app isn't installed, it will warn and ask you if you want to proceed with executing the script.

Running
*******

This is a bit of a different action, it's only purpose is to run the script.

.. code-block::

   $ installies run app_name


Extra Options
-------------

Outputting the Script's Code
****************************

You can output the script's code with the ``-o`` or ``--output-script`` flag.

.. code-block::

   $ installies install app_name -o


Specifying a Version
********************

You can specify a version of an app to install by appending "==version" to the end of the app name.

.. code-block::

   $ installies install python3==3.11.1

It is not guaranteed that the script actually installs the version you specified, so if you want to
confirm you can check the script code.


Getting a Script for another Distro, Architecture, or Shell
***********************************************************

To specify a distro, you can use the -d or --distro option.

.. code-block::

   $ installies install python3 --distro arch

To specify a architecture, you can use the -a or --architecture option.

.. code-block::

   $ installies install python3 --architechture arm

To specify a shell, you can use the -s or --shell option.

.. code-block::

   $ installies install python3 --shell zsh


Use Alternate Command to Run Script
***********************************

You can use the -c or --command option.

.. code-block::

   $ installies install python3 --command /path/to/shell 
