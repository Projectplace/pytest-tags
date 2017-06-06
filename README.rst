pytest-tags
===========

The pytest-tags plugin provides a way to mark your tests with tags.
This enhances the pytest's built-in collection system so that you can tag
tests across and within modules including test function level.

The tagging system works independently of the test names so it is not dependent on
any regex magic.

Installation
------------

To install pytest-tags using `pip <https://pip.pypa.io/>`_:

.. code-block:: bash

  $ pip install pytest-tags

Usage
*****

There a couple of ways you can use ``--tags``

    * Run with a single tag
    * Run with multiple tags
    * Filter using tags
    * Exclude tests

For the different options, please refer to the code-block at the bottom.

Single tag
__________

Using ``--tags failure`` will run the test ``test_failed_login``.

Using ``--tags login`` will run all the tests in the example.

Multiple tags
_____________

Using ``--tags failure password`` will run the tests ``test_failed_login`` and ``test_change_password``.

Filter using tags
_________________

Using ``--tags failure+user`` will run the test ``test_failed_login``.

Exclude tags
____________

Using ``--tags user 'not failure'`` will run all the tests marked with ``user``
but exclude the ones marked with ``failure`

**Note** If you're using the pytest-selenium plugin and specify ``driver`` you can mark tests with the browser
name to avoid running tests against non-compatible browsers.

Example::

    pytest --driver Firefox --tags user

will result in only ``test_failed_login`` being run.

.. code-block:: python

    import pytest

    pytestmark = pytest.mark.tags("login")

    @pytest.mark.tags("not firefox", "user")
    def test_login():

    @pytest.mark.tags("failure", "user")
    def test_failed_login():

    @pytest.mark.tags("password")
    def test_change_password():

