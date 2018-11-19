============
Contributing
============

Contributions are welcome and appreciated!
Every little bit helps, and credit will always be given.

.. _issue : https://github.com/nexB/saneyaml/issue
__ issue_

If you are new and want to find easy tickets to work on,
check `easy issues <https://github.com/nexB/saneyaml/labels/easy>`_

When contributing to this project  (such as code, bugs, documentation, etc.) you
agree to the Developer `Certificate of Origin <http://developercertificate.org/>`_
and its license (see the `apache-2.0.LICENSE <https://github.com/nexB/saneyaml/blob/develop/apache-2.0.LICENSE>`_ file).
The same approach is used by the Linux Kernel developers and several other projects.

For commits, it is best to simply add a line like this to your commit message,
with your name and email::

    Signed-off-by: Jane Doe <developer@example.com>

Please try to write a good commit message, see `good commit message wiki
<https://github.com/nexB/aboutcode/wiki/Writing-good-commit-messages>`_ for
details. In particular use the imperative for your commit subject: think that
you are giving an order to the codebase to update itself.


Feature requests and feedback
=============================

To send feedback or ask a question, `file an issue <issues_>`_

If you are proposing a feature:

* Explain how it would work.
* Keep the scope simple possible to make it easier to implement.
* Remember that your contributions are welcomed to implement this feature!


Chat with other developers
==========================

For other questions, discussions, and chats, we have:

- an official Gitter channel at https://gitter.im/aboutcode-org/discuss
  Gitter also has an IRC bridge at https://irc.gitter.im/
  This is the main place where we chat and meet.

- an official #aboutcode IRC channel on freenode (server chat.freenode.net)
  for scancode and other related tools. You can use your
  favorite IRC client or use the web chat at https://webchat.freenode.net/ .
  This is a busy place with a lot of CI and commit notifications that makes
  actual chat sometimes difficult!

- a mailing list at `sourceforge <https://lists.sourceforge.net/lists/listinfo/aboutcode-discuss>`_


Bug reports
===========

When `reporting a bug`__ please include:

* Your operating system name, version and architecture (32 or 64 bits).
* Your Python version.
* Your Saneyaml version.
* Any additional details about your local setup that might be helpful to
  diagnose this bug.
* Detailed steps to reproduce the bug, such as the commands you ran and a link
  to the code you are scanning.
* The errors messages or failure trace if any.
* If helpful, you can add a screenshot as an issue attachment when relevant or
  some extra file as a link to a `Gist <https://gist.github.com>`_.


Documentation improvements
==========================

Documentation can come in the form of wiki pages, docstrings, blog posts,
articles, etc. Even a minor typo fix is welcomed. 
See also extra documentation on the `Wiki <https://github.com/nexB/saneyaml/wiki>`_.


Pull Request Guidelines
-----------------------

If you need a code review or feedback while you are developing the code just
create a pull request. You can add new commits to your branch as needed.

For merging, your request would need to:

1. Include unit tests that are passing (run ``py.test``).
2. Update documentation as needed for new API, functionality etc. 
3. Add a note to ``CHANGELOG.rst`` about the changes.
4. Add your name to ``AUTHORS.rst``.


Test tips
---------

To run a subset of test functions containing test_myfeature in their name use::

    py.test -k test_myfeature

To run tests verbosely, displaying all print statements to terminal::

    py.test  -vvs
