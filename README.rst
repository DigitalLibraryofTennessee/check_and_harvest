======================
DLTN Check and Harvest
======================

.. image:: https://travis-ci.org/DigitalLibraryofTennessee/check_and_harvest.png
    :alt: TravisCI badge
.. image:: https://badge.fury.io/py/dltn-checker.svg
    :target: https://badge.fury.io/py/dltn-checker
    :alt: pypi badge


-----
About
-----

Tests whether records from an OAI-PMH feed pass minimum requirements of DLTN and optionally harvests only the good
records from a request to disk so that they can be added to Repox and included in the DPLA.

-------
Install
-------

Running with Builtin Argument Parsing from a CLI
================================================

If you want to do it this way, you're going to need to clone this.  It's also suggested to  build this with pipenv.

.. code-block:: console

    git clone https://github.com/DigitalLibraryofTennessee/check_and_harvest
    cd check_and_harvest
    pipenv install
    pipenv shell

Using OAIChecker from the dltnchecker module
============================================

If you're cool :sunglasses: :

.. code-block:: console

    pipenv install dltn_checker

Otherwise:

.. code-block:: console

    pip install dltn_checker


------------------------------------------
Examples with the Built In Argument Parser
------------------------------------------

1. Check for bad DC records in an entire OAI-PMH feed.

.. code-block:: console

    python run.py -e http://my-oai-endpoint:8080/OAIHandler -m oai_dc

2. Check and harvest good DC records from an entire OAI-PMH feed.

.. code-block:: console

    python run.py -e http://my-oai-endpoint:8080/OAIHandler -m oai_dc -H True

3. Check and harvest good xoai records from a specific set.

.. code-block:: console

    python run.py -e http://my-oai-endpoint:8080/OAIHandler -m xoai -s my_awesome_xoai_set -H True

4. Check and harvest good MODS records from an entire provider in Repox.

.. code-block:: console

    python run.py -e http://my-oai-endpoint:8080/OAIHandler -m MODS -p CrossroadstoFreedomr0 -H True

5. Check and harvest good MODS records from a provider and ensure that the thumbnail and link to the objects resolve.

.. code-block:: console

    python run.py -e http://my-oai-endpoint:8080/OAIHandler -m MODS -p CrossroadstoFreedomr0 -H True -tu True

6. Check and harvest good MODS records from a provider, ensure that the thumbnail and link to object are good, and limit
to records added since January 1, 2015.

.. code-block:: console

    python run.py -e http://my-oai-endpoint:8080/OAIHandler -m MODS -p CrossroadstoFreedomr0 -H True -tu True -f 2015-01-01

7. Harvest records from hatch3 in CMHF if the record meets our minimum qualifications for metadata sharing and is not
restricted.

.. code-block:: console

    python run.py -e http://digi.countrymusichalloffame.org/oai/oai.php -m oai_qdc -w good -tr True -s hatch3

----------------------------------------------------
Examples using the OAIChecker Class from dltnchecker
----------------------------------------------------

Check a set to see if there are any bad files in a set.

.. code-block:: python

    from dltnchecker.harvest import OAIChecker
    request = OAIChecker("https://dpla.lib.utk.edu/repox/OAIHandler", "crossroads_sanitation", "MODS")
    request.list_records()
    print(request.bad_records)

By default, this will try to download the good files to a directory called output. If you don't want to download, you
need to pass an additional parameter called harvest and set to False.

.. code-block:: python

    from dltnchecker.harvest import OAIChecker
    request = OAIChecker("https://dpla.lib.utk.edu/repox/OAIHandler", "crossroads_sanitation", "MODS", harvest=False)
    request.list_records()
    print(request.bad_records)
