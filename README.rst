======================
DLTN Check and Harvest
======================

.. image:: https://travis-ci.org/DigitalLibraryofTennessee/check_and_harvest.png
    :alt: TravisCI badge


-----
About
-----

Tests whether records from an OAI-PMH feed pass minimum requirements of DLTN and optionally harvests only the good
records from a request to disk so that they can be added to Repox and included in the DPLA.

--------
Requires
--------

* python 3.7
* pipenv (strongly recommend)

-------
Install
-------

You're going to need to clone this down and build this with pipenv.

.. code-block:: console

    $ git clone https://github.com/DigitalLibraryofTennessee/check_and_harvest
    $ cd check_and_harvest
    $ pipenv install
    $ pipenv shell

--------
Examples
--------

1. Check for bad DC records in an entire OAI-PMH feed.

.. code-block:: console

    $ python run -e http://my-oai-endpoint:8080/OAIHandler -m oai_dc

2. Check and harvest good DC records from an entire OAI-PMH feed.

.. code-block:: console

    $ python run -e http://my-oai-endpoint:8080/OAIHandler -m oai_dc -H True

3. Check and harvest good xoai records from a specifc set.

.. code-block:: console

    $ python run -e http://my-oai-endpoint:8080/OAIHandler -m xoai -s my_awesome_xoai_set -H True

4. Check and harvest good MODS records from an entire provider in Repox.

.. code-block:: console

    $ python run -e http://my-oai-endpoint:8080/OAIHandler -m MODS -p CrossroadstoFreedomr0 -H True
