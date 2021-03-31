<<<<<<< HEAD
========
saneyaml
========

This micro library is a PyYaml wrapper with sane behaviour to read and
write readable YAML safely, typically when used with configuration files.

With saneyaml you can dump readable and clean YAML and load safely any YAML
preserving ordering and avoiding surprises of type conversions by loading
everything except booleans as strings.
Optionally you can check for duplicated map keys when loading YAML.

Works with Python 3. Requires PyYAML 5.x.

License: apache-2.0
Homepage_url: https://github.com/nexB/saneyaml

Usage::

pip install saneyaml

>>> from  saneyaml import load as l
>>> from  saneyaml import dump as d
>>> a=l('''version: 3.0.0.dev6
... 
... description: |
...     AboutCode Toolkit is a tool to process ABOUT files. An ABOUT file
...     provides a way to document a software component.
... ''')
>>> a
OrderedDict([
    (u'version', u'3.0.0.dev6'), 
    (u'description', u'AboutCode Toolkit is a tool to process ABOUT files. '
    'An ABOUT file\nprovides a way to document a software component.\n')])

>>> pprint(a.items())
[(u'version', u'3.0.0.dev6'),
 (u'description',
  u'AboutCode Toolkit is a tool to process ABOUT files. An ABOUT file\nprovides a way to document a software component.\n')]
>>> print(d(a))
version: 3.0.0.dev6
description: |
  AboutCode Toolkit is a tool to process ABOUT files. An ABOUT file
  provides a way to document a software component.

=======
A Simple Python Project Skeleton
================================
This repo attempts to standardize our python repositories using modern python
packaging and configuration techniques. Using this `blog post`_ as inspiration, this
repository will serve as the base for all new python projects and will be adopted to all 
our existing ones as well.

.. _blog post: https://blog.jaraco.com/a-project-skeleton-for-python-projects/

Usage
=====
A brand new project
-------------------
.. code-block:: bash

    git init my-new-repo
    cd my-new-repo
    git pull git@github.com:nexB/skeleton

    # Create the new repo on GitHub, then update your remote
    git remote set-url origin git@github.com:nexB/your-new-repo.git

From here, you can make the appropriate changes to the files for your specific project.

Update an existing project
---------------------------
.. code-block:: bash

    cd my-existing-project
    git remote add skeleton git@github.com:nexB/skeleton
    git fetch skeleton
    git merge skeleton/main --allow-unrelated-histories

This is also the workflow to use when updating the skeleton files in any given repository.
>>>>>>> refs/remotes/skeleton/main
