# Staying in sync with plotnine

`plotnine-extra` is an **extension package**, not a fork of plotnine. There is
no `plotnine/` source tree in this repository — plotnine is an ordinary runtime
dependency (see `pyproject.toml`). That is the single most important fact for
staying in sync: **"integrating new plotnine commits" is a dependency version
bump, not a git merge.** There is nothing to rebase and nothing of ours to
clobber.

This document explains how to keep up with plotnine safely, and why the one
place we broke is the one place we had diverged from that rule.

## The failure we fixed, and the lesson

Plot composition used to be **vendored**: `plotnine_extra/composition/` held a
copy of plotnine's composition code. plotnine then shipped composition natively
— the `|`, `/`, `-`, `+` operators live on `plotnine.ggplot`, so `p1 | p2`
builds a *plotnine* `Beside`. Our vendored `plot_layout`/`Wrap` were a separate
lineage that could never own those operators, so mixing them crashed.

The fix was to stop vendoring and re-export from `plotnine.composition`
(`plotnine_extra/composition/__init__.py`). Now the operators and the objects
they build come from the same source and cannot disagree. Syncing composition
from upstream is now automatic: it rides along with the installed plotnine.

**Lesson: don't vendor plotnine code. Delegate to it.** Copying upstream code is
what creates a divergent branch you then have to merge.

## Where we are still coupled (the real sync risk)

Delegation solves composition, but several extension modules reach into
plotnine's **internal (underscore) APIs**, which plotnine changes without
notice between releases. These are the surfaces to watch on every plotnine
bump. Concrete breaks seen going from plotnine 0.15 → 0.16:

| Module | Internal it uses | 0.15 → 0.16 change |
| --- | --- | --- |
| `stats/` (`stat_pwc`, `stat_compare`, `stat_compare_means`) | stat instance kwargs | `self._kwargs` → `self._raw_kwargs` |
| `guides/` (`guide_stringlegend`) | theme `guide_text` element | `.ha`/`.va` attributes changed |
| `facets/` (`facet_manual`) | `facets/strips.py`, `facets/facet.py` layout hooks | strip/axes access signatures changed |
| `animation.py` | figure/draw internals | verify each bump |

The stats break is already handled version-tolerantly via
`plotnine_extra/stats/_common.py::drop_forwarded_kwarg` (it looks up both
attribute names). The guides/facets breaks are **not yet migrated** — they work
on stable plotnine (0.15.x) and only break on the 0.16 alphas, so they are
deferred until plotnine 0.16 is adopted (see "Version policy" below).

When touching these modules, prefer plotnine's **public** API. Every use of an
underscore-prefixed plotnine name is a future sync break waiting to happen; add
a small version-tolerant shim (like `drop_forwarded_kwarg`) rather than reading
the attribute directly.

## Version policy

- **Dependency floor:** `plotnine>=0.15.3,<0.17` (`pyproject.toml`). We stay
  installable on stable plotnine and never force a pre-release.
- **Composition extras** (`plot_layout`, `plot_annotation`, `Wrap`, and the
  `ggarrange(layout=...)` / `annotate_figure` helpers) require plotnine `>=0.16`.
  On older plotnine they resolve to a stub that raises a clear upgrade error, so
  `import plotnine_extra` still works and only the extras are gated.
- **When plotnine 0.16.0 ships stable:** raise the floor to `>=0.16`, migrate
  the guides/facets internals above, and drop the gating stubs.

## Routine sync workflow

Fetch upstream (the `upstream` remote already points at `has2k1/plotnine`):

```bash
git fetch upstream --tags
```

1. **See what changed.** Compare the plotnine version you support against the
   latest tag, and skim its changelog for composition/stat/guide/facet
   internals:
   ```bash
   git log --oneline v0.15.7..v0.16.0a11 -- plotnine/stats plotnine/guides plotnine/facets
   ```
2. **Bump and test.** Change the floor in `pyproject.toml`, then run the suite
   against the new plotnine in a throwaway venv (see below). No code merge.
3. **Fix coupling, not composition.** Composition rides the dependency. If tests
   fail, they will point at the internal-API surfaces in the table above.
4. **Regenerate image baselines** only if rendering legitimately changed, and do
   it in an environment matching CI (Linux + the matplotlib CI resolves).
   Baselines for matplotlib ≥3.11 use the `-mpl311` filename suffix (see
   `tests/conftest.py::select_baseline_image`).

### Test against an unreleased plotnine without touching your env

```bash
python -m venv /tmp/pe-pre && source /tmp/pe-pre/bin/activate
pip install --pre "plotnine>=0.16.0a1,<0.17" scipy pytest
pip install --no-deps -e .        # keep the pre-release plotnine
python -m pytest tests/ -q
```

The composition image tests self-skip when the installed plotnine lacks the
0.16 composition layout API, so a stable-plotnine run and a pre-release run both
stay meaningful.

## Recommended: a pre-release early-warning CI lane

The internal-API coupling means plotnine can break us *before* we intend to
upgrade. Add a non-blocking CI job that installs `--pre` plotnine and runs the
suite, so the next break (the next `_kwargs`-style rename) surfaces as a warning
on our schedule instead of a bug report after plotnine releases. Keep it
`continue-on-error: true` so it never blocks the stable-plotnine matrix.

## What the `upstream` remote is *not* for

The `upstream` remote is handy for reading plotnine's source, diffing internals
across versions, and cherry-picking a specific fix into a local patch. It is
**not** a branch to merge into `main`. Do not merge plotnine's source tree into
this package — that recreates the vendoring problem this whole document exists
to prevent.
