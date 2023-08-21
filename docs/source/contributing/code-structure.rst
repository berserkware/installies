Code Structure
==============

This is a rough guidance to help you navigate the codebase.

Python
------

``/blueprints``
***************
The views for the site. The blueprints containing the routes are in the
``/blueprints/<blueprint_name>/blueprint.py``. The other files are for
defining the views.

``/database``
*************
Functions for creating/dropping tables in the database.

``/forms``
**********
The forms for the site. These are all inherited from the ``Form`` class defined in the ``/forms/base.py`` file.

``/groups``
***********
Groups for retrieving objects from the database. These are all inherited from the ``Group`` class
defined in the ``/groups/base.py`` file.

``/lib``
********
Miscellaneous code.

``/models``
***********
The peewee models for the site.

``/validators``
***************
The validator classes for validating input from users. These are all inherited from the
``Validator`` class defined in the ``/validators/base.py`` file.

Other
-----

``/templates``
**************
The templates for the site.

``/static``
***********
The static files for use in the frontend.
