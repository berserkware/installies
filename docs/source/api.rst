API
===

This is a reference for the Installies web API. It is used for the CLI.

Apps
----

``/api/apps``
^^^^^^^^^^^^^

This is an endpoint for getting data about apps.

URL Parameters
^^^^^^^^^^^^^^

.. list-table::

 * - **Name**
   - **Description**
 * - name
   - The name of the app.
 * - display_name
   - The display name of the app.
 * - creation_date
   - The date and time the app was created.
 * - last_modified
   - The date and time the app was last modified.
 * - search-in
   - The attribute to search in. You can search in the name, description, maintainers, and submitter.
 * - k
   - The keywords to search.
 * - distro
   - The distro the script supports.
 * - arch
   - The architecture the script supports.
 * - sort-by
   - The attribute to sort by. It can be by the name, description, creation date, last modified, and submitter.
 * - order-by
   - What to order the objects by. Can be "asc" (ascending), or "desc" (descending). defaults to ascending.
 * - page
   - The page of apps to get.
 * - per-page
   - The amount of apps per page.

Response
^^^^^^^^

.. code-block:: json

    {
	"apps": [
	    {
	        "creation_date": "2023-08-07 07:02:39",
	        "current_version": "",
	        "description": "The python3 programming language.",
	        "display_name": "Python3",
	        "id": 1,
	        "last_modified": "2023-08-09 08:21:03",
	        "name": "python3",
	        "submitter": "berserkware"
	    }
        ]  
   }

Scripts
-------
   
``/api/apps/<app_name>/scripts``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A endpoint for getting data about scripts.

URL Parameters
^^^^^^^^^^^^^^

.. list-table::

 * - **Name**
   - **Description**
 * - id
   - The script's id.
 * - version
   - The scripts's version.
 * - creation_date
   - The date and time the script was created.
 * - last_modified
   - The date and time the script was last modified.
 * - search-in
   - The attribute to search in. You can search in the method, maintainers, and the submitter.
 * - k
   - The keywords to search.
 * - distro
   - The distro the script supports.
 * - arch
   - The architecture the script supports.
 * - actions
   - The actions the script supports.
 * - sort-by
   - The attribute to sort by. It can be by the score, version, last_modified, creation_date, and submitter.
 * - order-by
   - What to order the objects by. Can be "asc" (ascending), or "desc" (descending). defaults to ascending.
 * - page
   - The page of scripts to get.
 * - per-page
   - The amount of scripts per page.

Response
^^^^^^^^

.. code-block:: json

    {
      "scripts": [
          {
              "actions": [
                  "install",
                  "remove",
                  "update"
              ],
              "content": "function install {\n\techo \"install\"\n}\n\nfunction remove {\n\techo \"remove\"\n}\n\nfunction update {\n\techo \"update\"\n}\n\nif [ \"$1\" == \"install\" ]; then\n    install\nfi\n\nif [ \"$1\" == \"remove\" ]; then\n    remove\nfi\n\nif [ \"$1\" == \"update\" ]; then\n    update\nfi\n",
	      "creation_date": "2023-10-22 05:39:03",
              "for_version": "3.11.3",
              "id": 1,
              "last_modified": "2023-08-09 06:42:30",
	      "score": 1,
              "method": "Installs with pacman.",
	      "shell": "bash",
              "submitter": "berserkware",
              "supported_distros": {
                  "*": [
                      "arch"
                  ]
              }
         },
    }


The supported_distros dictionary has the architecture as its keys, and the distros as the values in the list.
