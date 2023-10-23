Contributing to Installies
==========================

Installies is written in Python, and uses the Flask web framework. Instead of using flasks
function-based views, Installies uses a django-like class-based view system. The only exception
to this is the auth routes, which use the function-based views.

Installies uses `peewee ORM <http://docs.peewee-orm.com/en/latest/>`_ for its models.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   code-structure.rst
   running.rst
