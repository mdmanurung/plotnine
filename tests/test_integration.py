"""
Integration tests for plotnine_extra package.

Tests that the package properly re-exports plotnine's API and that
extra components work with plotnine's ggplot objects.
"""

import pandas as pd


def test_plotnine_reexports():
    """Verify plotnine public API is re-exported."""
    from plotnine_extra import (  # noqa: F401
        coord_cartesian,
        element_blank,
        facet_wrap,
        geom_bar,
        ggplot,
        guide_legend,
        labs,
        position_dodge,
        scale_color_brewer,
        stat_bin,
        theme,
        theme_bw,
    )

    # All should be importable without error
    assert callable(ggplot)
    assert callable(coord_cartesian)
    assert callable(facet_wrap)
    assert callable(geom_bar)
    assert callable(guide_legend)
    assert callable(labs)
    assert callable(position_dodge)
    assert callable(scale_color_brewer)
    assert callable(stat_bin)
    assert callable(theme)
    assert callable(theme_bw)


def test_star_import_reexports_plotnine_and_extras():
    """Verify star import matches the documented convenience API."""
    namespace = {}
    exec("from plotnine_extra import *", namespace)

    assert callable(namespace["ggplot"])
    assert callable(namespace["aes"])
    assert callable(namespace["geom_bar"])
    assert callable(namespace["geom_pointdensity"])


def test_extra_geoms_with_ggplot():
    """Verify extra geoms work with plotnine ggplot."""
    from plotnine_extra import aes, geom_pointdensity, ggplot

    data = pd.DataFrame({"x": [1, 2, 3], "y": [1, 2, 3]})
    p = ggplot(data, aes("x", "y")) + geom_pointdensity()
    # Should create without error
    assert p is not None


def test_extra_composition_imports():
    """Verify composition module is importable."""
    from plotnine_extra.composition import (  # noqa: F401
        Beside,
        Compose,
        Stack,
        Wrap,
        plot_annotation,
        plot_layout,
        plot_spacer,
    )

    assert Compose is not None
    assert Beside is not None
    assert Stack is not None
    assert Wrap is not None
    assert plot_layout is not None
    assert plot_annotation is not None
    assert plot_spacer is not None


def test_version():
    """Verify version is set."""
    import plotnine_extra

    assert plotnine_extra.__version__ == "0.3.1"
