====================================
Miscellaneous Operations Using sfftk
====================================

.. contents::

Viewing File Metadata
=====================

.. code:: bash

    sff view <file>

Settings Configurations
=======================

Some of the functionality provided by sfftk relies on persistent configurations. In the section we outline all you need to know to work with sfftk configurations.

Configurations are handled using the ``config`` utility with several subcommands.

.. code:: bash 

	sff config [subcommand]

For example:

.. code:: bash

	(sfftk) pkorir@pkorir-tarakimu:docs $ sff config list
	Fri Jan 19 14:03:34 2018	Reading configs from /Users/pkorir/.sfftk/sff.conf
	Fri Jan 19 14:03:34 2018	Listing all 3 configs...
	__TEMP_FILE          = ./temp-annotated.json
	__TEMP_FILE_REF      = @
	NAME                 = VALUE

Configuration commands
----------------------

Listing available configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sff config list

Getting a single configuration value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sff config get CONFIG_NAME

Setting a single configuration value
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sff config set CONFIG_NAME CONFIG_VALUE

Deleting a single configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sff config del CONFIG_NAME

Clearing all configurations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: bash

	sff config clear

Where configurations are stored
---------------------------------

sfftk ships with a config file called ``sff.conf`` which is located in the root of the package. 
In some cases this might be a read-only location e.g. if installed ``/usr/local/lib/python2.7/site-packages``. 
Therefore, default read-only configurations will be obtained from this file. 
However, if the user would like to write new configs they will be written to ``~/sfftk/sff.conf``. 
Additionally, a user may specify a third location using the ``-p/--config-path`` flag to either read or write a new config. 
Correspondingly, custom configs will only be used if the ``-p/--config-path`` flag is used.

For example

.. code:: bash

	sff config set NAME VAL
	
will add the line ``NAME=VAL`` to ``~/.sfftk/sff.conf`` but 

.. code:: bash

	sff config set NAME VAL --config-path /path/to/sff.conf
	
will add it to ``/path/to/sff.conf`` (provided it is writable by the current user).

The order of precedence, therefore is:

- custom configs specified with ``-p/--config-path``;

- user configs in ``~/.sfftk/sff.conf``; then

- packaged configs (fallback if none of the above are present);


Running Unit Tests
==================

.. code:: bash

    sff tests [tool]

``<tool>`` is optional and if left out all tests for all packages are run.
