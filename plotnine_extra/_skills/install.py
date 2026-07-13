"""Install the bundled plotnine-extra agent skill.

The package ships a Claude/Codex-compatible skill, but those tools do not scan
Python site-packages for skills. This module exposes the
``plotnine-extra-install-skills`` command, which copies the bundled skill into
one or both personal skill roots.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

SKILL_NAME = "plotnine-extra"
TARGETS = ("claude", "codex")


def _bundled_skill_dir() -> Path:
    """Return the path to the bundled skill directory."""

    return Path(__file__).resolve().parent / "data"


def _default_dest(target: str) -> Path:
    """Return the default install destination for a supported agent target."""

    if target == "claude":
        return Path.home() / ".claude" / "skills" / SKILL_NAME
    if target == "codex":
        return Path.home() / ".codex" / "skills" / SKILL_NAME
    raise ValueError(f"Unknown target: {target}")


def install_skill(
    dest: Path | None = None,
    *,
    target: str = "claude",
    force: bool = False,
) -> Path:
    """Copy the bundled skill into a Claude or Codex skills directory.

    Parameters
    ----------
    dest:
        Destination directory. If ``None``, the default root for ``target`` is
        used.
    target:
        Either ``"claude"`` or ``"codex"``.
    force:
        Replace an existing destination directory when true.
    """

    if target not in TARGETS:
        raise ValueError(
            "target must be one of {}.".format(", ".join(TARGETS))
        )

    src = _bundled_skill_dir()
    if not (src / "SKILL.md").is_file():
        raise FileNotFoundError(
            "Bundled skill not found at {}. The package may be installed "
            "without its skill data.".format(src)
        )

    if dest is None:
        dest = _default_dest(target)

    if dest.exists():
        if not force:
            raise FileExistsError(
                "{} already exists. Re-run with --force to overwrite.".format(
                    dest
                )
            )
        shutil.rmtree(dest)

    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        src,
        dest,
        ignore=shutil.ignore_patterns(".ipynb_checkpoints", "__pycache__"),
    )
    return dest


def install_targets(
    target: str = "both",
    *,
    dest: Path | None = None,
    force: bool = False,
) -> list[tuple[str, Path]]:
    """Install the bundled skill for one or both supported agent targets."""

    if target == "both":
        if dest is not None:
            raise ValueError("--dest can only be used with one target.")
        targets = TARGETS
    elif target in TARGETS:
        targets = (target,)
    else:
        raise ValueError("target must be claude, codex, or both.")

    destinations = [
        (name, dest if dest is not None else _default_dest(name))
        for name in targets
    ]
    if not force:
        existing = [path for _, path in destinations if path.exists()]
        if existing:
            existing_text = ", ".join(str(path) for path in existing)
            raise FileExistsError(
                "{} already exists. Re-run with --force to overwrite.".format(
                    existing_text
                )
            )

    return [
        (name, install_skill(dest=path, target=name, force=force))
        for name, path in destinations
    ]


def main(argv: list[str] | None = None) -> int:
    """Command-line entry point for ``plotnine-extra-install-skills``."""

    parser = argparse.ArgumentParser(
        prog="plotnine-extra-install-skills",
        description="Install the bundled plotnine-extra skill for Claude Code "
        "and/or Codex.",
    )
    parser.add_argument(
        "--target",
        choices=("both", *TARGETS),
        default="both",
        help="Agent target to install for (default: both).",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=None,
        help="Destination directory; valid only when --target is not both.",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite an existing installed skill.",
    )
    parser.add_argument(
        "--print-path",
        action="store_true",
        help="Print the bundled skill directory and exit without installing.",
    )
    args = parser.parse_args(argv)

    if args.print_path:
        print(_bundled_skill_dir())
        return 0

    try:
        installed = install_targets(
            target=args.target,
            dest=args.dest,
            force=args.force,
        )
    except (FileExistsError, FileNotFoundError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    for target, dest in installed:
        print(f"Installed plotnine-extra skill for {target} to {dest}")
    print("Restart the agent session for the skill metadata to be reloaded.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
