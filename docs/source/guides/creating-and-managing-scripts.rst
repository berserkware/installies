Creating and Managing Scripts
=============================

Scripts are how Installies installs, removes, updates, or compiles apps. This is a guide on how
to create and manage scripts.

Creating Scripts
----------------

.. image:: ../_static/add-script.png
  :alt: Add Script Form

You can create a script by clicking the "Add Script" link on the app sidebar. This will
take you to the add script form. 

Actions
*******
The Actions input should contain a comma-separated list of things that that script does. Some
common actions are:

 - install: installs the app.
 - remove: removes the app.
 - update: updates the app.
 - compile: compiles the app.
 - run: An action the can be used for scripts to just run code.

Shell
*****
You can select a shell with the shell input.

Description
***********
The description input should contain a basic description of how the script does what it does.
e.g. "Installs with pacman" or "Compiles from source.".

Supported Distros
*****************

In each row in the supported distros table, you can add the distros and the architechture that
this script supports. Adding another row allows you to add distros that support different distros.
You can remove a row of distros by clicking the remove button on the left of the row. You can
replace the distro or architecture name with an asterisk symbol to match any distro or
architecture.

Getting the Distro Names
^^^^^^^^^^^^^^^^^^^^^^^^

You can get the name to put in the distro option by getting the id of the distro through the
following command.

.. code-block:: bash

    $ grep ^ID= /etc/os-release
    ID=arch

Getting the Architecture Names
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can get the name to put in the architecture option by getting the architecture through
the following command.

.. code-block:: bash

    $ uname -m
    x86_64

Content
*******

The content textbox is where you put the actual script code. The script should take one of the
supported actions as the first arg. If the user does not input one of the script's supported
actions, the script should return an error, and tell the user to enter one of the supported actions.

You do not need to add a shebang to the start of the script, as this is added automatically.

If you select the "Use Default Function Matcher" option under the script content, a block of code
will be added at the end to match functions to actions. If you enable this, you code should look
something like this (assuming your script is using bash):

.. code-block:: bash

   # put code that will run for any action here

   function install {
	# put install code here
   }

   function remove {
	# put remove code here
   }

   function update {
	# put update code here
   }

If you are using the bash shell, then the matcher code will look something like this.

.. code-block:: bash

   if [ "$1" == "install" ]; then
	install
	exit
   fi
   if [ "$1" == "remove" ]; then
	remove
	exit
   fi
   if [ "$1" == "update" ]; then
	update
	exit
   fi

   echo "Please re-run the script with one of the following actions as the first arg: install remove update."

For App Version
***************

This is an optional input for specifying a version of the app that the script installs.

Managing Scripts
----------------

Maintainers
***********

To manage scripts you must be a maintainer. You can add a maintainer by clicking the link in
the script options. You have to remember that maintainers you add will have the exact same
permissions as you, so don't add just anyone. The script submitter doesn't have any permission
to edit the script, unless they are a maintainer.

You can remove maintainers by clicking remove next to their name in the maintainer list.

Editing
*******

You can edit scripts by clicking the edit link in the script options.

Deleting
********

You can delete scripts by clicking the delete link in the script options.
