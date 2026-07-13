Facets and Strips
=================

.. currentmodule:: plotnine_extra

Extended Facets
---------------

The extended facets add selected ggh4x-style behaviours on top of plotnine's
facet system. Exact layout parity is limited by the extension points available
in plotnine.

facet_grid2
~~~~~~~~~~~

.. autoclass:: facet_grid2
   :members:
   :undoc-members:
   :show-inheritance:

facet_wrap2
~~~~~~~~~~~

.. autoclass:: facet_wrap2
   :members:
   :undoc-members:
   :show-inheritance:

facet_nested
~~~~~~~~~~~~

.. autoclass:: facet_nested
   :members:
   :undoc-members:
   :show-inheritance:

facet_nested_wrap
~~~~~~~~~~~~~~~~~

.. autoclass:: facet_nested_wrap
   :members:
   :undoc-members:
   :show-inheritance:

facet_manual
~~~~~~~~~~~~

.. autoclass:: facet_manual
   :members:
   :undoc-members:
   :show-inheritance:

Per-panel Scales
----------------

Per-panel position scales are attached with ``+ facetted_pos_scales(...)`` or
through ``scale_x_facet`` and ``scale_y_facet``. Use free or independent facet
scales so plotnine can apply the per-panel replacements.

facetted_pos_scales
~~~~~~~~~~~~~~~~~~~

.. autofunction:: facetted_pos_scales

scale_x_facet
~~~~~~~~~~~~~

.. autofunction:: scale_x_facet

scale_y_facet
~~~~~~~~~~~~~

.. autofunction:: scale_y_facet

Strips
------

Strip helpers are accepted by the extended facets where plotnine permits custom
strip rendering. Unsupported strip and layout combinations raise explicit
errors rather than being ignored.

strip_nested
~~~~~~~~~~~~

.. autoclass:: strip_nested
   :members:
   :undoc-members:
   :show-inheritance:

strip_themed
~~~~~~~~~~~~

.. autoclass:: strip_themed
   :members:
   :undoc-members:
   :show-inheritance:

strip_split
~~~~~~~~~~~

.. autoclass:: strip_split
   :members:
   :undoc-members:
   :show-inheritance:

strip_tag
~~~~~~~~~

.. autoclass:: strip_tag
   :members:
   :undoc-members:
   :show-inheritance:
