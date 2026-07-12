from __future__ import annotations

from plotnine.ggplot import ggplot

from ._compose import Compose


class Wrap(Compose):
    """
    Wrap plots or compositions into a grid

    **Usage**

        plot + plot
        plot + composition
        composition + plot
        composition + composition

    Typically, you will use this class through the `+` operator.

    Parameters
    ----------
    items:
        The objects to be arranged (composed)
    nrow:
        Number of rows in the composition
    ncol:
        Number of cols in the composition

    See Also
    --------
    plotnine_extra.composition.Beside
    plotnine_extra.composition.Stack
    plotnine_extra.composition.plot_spacer
    plotnine_extra.composition.Compose
    """

    def __add__(self, rhs):
        """
        Add rhs into the wrapping composition
        """
        if not isinstance(rhs, (ggplot, Compose)):
            return super().__add__(rhs)

        return Wrap([*self, rhs]) + self.layout + self.annotation

    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """
        from ._beside import Beside

        return Beside([self, rhs])

    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a row
        """
        from ._stack import Stack

        return Stack([self, rhs])
