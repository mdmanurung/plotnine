Installation
============

Requirements
------------

* Python ≥ 3.10
* plotnine ≥ 0.15.3
* scipy ≥ 1.10.0

Install from PyPI
-----------------

The recommended way to install **plotnine-extra** is from PyPI:

.. code-block:: bash

   pip install plotnine-extra

This will also pull in the required dependencies (``plotnine`` and
``scipy``).

Claude Code and Codex skills
----------------------------

The package includes a bundled agent skill for Claude Code and Codex. It gives
coding agents package-specific guidance for facets, guides, statistical
annotations, composition, animation, and common API traps.

Python packages should not write into user agent configuration directories as a
side effect of ``pip install``. After installing or upgrading the package, run:

.. code-block:: bash

   plotnine-extra-install-skills

By default this installs the skill into both
``~/.claude/skills/plotnine-extra/`` and
``~/.codex/skills/plotnine-extra/``. Use ``--target claude`` or
``--target codex`` to install for only one agent, and ``--force`` to refresh an
existing installed copy after an upgrade.

To inspect the bundled skill path without copying files:

.. code-block:: bash

   plotnine-extra-install-skills --print-path

Install from source
-------------------

To install the latest development version directly from GitHub:

.. code-block:: bash

   pip install git+https://github.com/mdmanurung/plotnine-extra.git

Or clone the repository and install in editable mode:

.. code-block:: bash

   git clone https://github.com/mdmanurung/plotnine-extra.git
   cd plotnine-extra
   pip install -e .

Verify the installation
-----------------------

.. code-block:: python

   import plotnine_extra
   print(plotnine_extra.__version__)
