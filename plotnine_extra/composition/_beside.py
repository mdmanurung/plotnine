from __future__ import annotations

from typing import TYPE_CHECKING

from ._compose import Compose

if TYPE_CHECKING:
    from plotnine.ggplot import ggplot


class Beside(Compose):
    """
    Place plots or compositions side by side

    **Usage**

        plot | plot
        plot | composition
        composition | plot
        composition | composition

    Typically, you will use this class through the `|` operator.

    See Also
    --------
    plotnine_extra.composition.Stack
    plotnine_extra.composition.Wrap
    plotnine_extra.composition.plot_spacer
    plotnine_extra.composition.Compose
    """

    def __or__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a column
        """
        # This is adjacent or i.e. (OR | rhs) so we collapse
        # the operands into a single operation
        return Beside([*self, rhs]) + self.layout + self.annotation

    def __truediv__(self, rhs: ggplot | Compose) -> Compose:
        """
        Add rhs as a row
        """
        from ._stack import Stack

        return Stack([self, rhs])

    def __add__(self, rhs):
        """
        Add rhs into the besides composition
        """
        from plotnine import ggplot

        if not isinstance(rhs, (ggplot, Compose)):
            return super().__add__(rhs)

        return self | rhs
