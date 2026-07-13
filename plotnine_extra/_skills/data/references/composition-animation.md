# Composition and Animation

`plotnine-extra` lets users combine plotnine plots with operators:

```python
from plotnine import aes, geom_point, ggplot
from plotnine.data import mtcars
from plotnine_extra import plot_annotation, plot_layout

p1 = ggplot(mtcars, aes("wt", "mpg")) + geom_point()
p2 = ggplot(mtcars, aes("hp", "mpg")) + geom_point()

(p1 | p2) + plot_layout(widths=[1, 2]) + plot_annotation(title="Cars")
```

Operator meanings:

- `p1 | p2`: place plots side by side with `Beside`.
- `p1 / p2`: stack plots vertically with `Stack`.
- `p1 + p2`: wrap plots into a grid with `Wrap`.
- `p1 - p2`: place plots side by side at the same nesting level.
- `composition & theme_or_layer`: add to all plots in a composition.
- `composition * theme_or_layer`: add to top-level plots only.

Use `plot_layout(nrow=, ncol=, widths=, heights=)` for grid and sizing control,
`plot_annotation(title=, subtitle=, caption=, footer=)` for composition labels,
and `plot_spacer()` for blank slots.

## Animation

`PlotnineAnimation` turns a sequence of plotnine plots into a Matplotlib
animation:

```python
from plotnine_extra import PlotnineAnimation

ani = PlotnineAnimation(plots, interval=200)
ani.save("animation.gif")
```

Keep axis limits stable across frames when the visual comparison depends on
position or scale.
