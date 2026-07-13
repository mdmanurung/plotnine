from __future__ import annotations

import re
from pathlib import Path

import pytest

from plotnine_extra._skills import install as install_mod
from plotnine_extra._skills.install import (
    _bundled_skill_dir,
    _default_dest,
    install_skill,
    install_targets,
    main,
)


def _link_targets(text: str) -> list[str]:
    return re.findall(r"\]\(([^)]+\.md)\)", text)


def _seed_fake_skill(root: Path) -> Path:
    (root / "references").mkdir(parents=True)
    (root / "SKILL.md").write_text(
        "---\nname: x\ndescription: y\n---\n\nbody\n"
    )
    (root / "references" / "foo.md").write_text("# foo\n")
    return root


def test_bundled_skill_dir_is_well_formed():
    data = _bundled_skill_dir()

    assert data.is_dir()
    assert (data / "SKILL.md").is_file()
    assert list((data / "references").glob("*.md"))


def test_skill_frontmatter_is_valid_for_agents():
    text = (_bundled_skill_dir() / "SKILL.md").read_text()
    frontmatter = text.split("---\n", 2)[1]
    fields = dict(
        re.findall(r"^(\w+):\s*(.*)$", frontmatter, flags=re.MULTILINE)
    )

    assert fields["name"] == "plotnine-extra"
    assert 0 < len(fields["description"]) <= 1536


def test_internal_markdown_links_resolve():
    data = _bundled_skill_dir()
    files = [data / "SKILL.md", *(data / "references").glob("*.md")]
    broken = []

    for file in files:
        for target in _link_targets(file.read_text()):
            resolved = (file.parent / target).resolve()
            if not resolved.is_file():
                broken.append(f"{file.name} -> {target}")

    assert broken == []


def test_install_claude_skill_into_fresh_dest(tmp_path):
    dest = tmp_path / "plotnine-extra"
    result = install_skill(dest=dest, target="claude")

    assert result == dest
    assert (dest / "SKILL.md").is_file()
    assert {path.name for path in (dest / "references").glob("*.md")} == {
        path.name
        for path in (_bundled_skill_dir() / "references").glob("*.md")
    }


def test_install_codex_skill_into_fresh_dest(tmp_path):
    dest = tmp_path / "plotnine-extra"
    result = install_skill(dest=dest, target="codex")

    assert result == dest
    assert (dest / "SKILL.md").is_file()


def test_install_existing_dest_raises_without_force(tmp_path):
    dest = tmp_path / "plotnine-extra"
    install_skill(dest=dest)

    with pytest.raises(FileExistsError):
        install_skill(dest=dest)


def test_install_force_replaces_stale_content(tmp_path):
    dest = tmp_path / "plotnine-extra"
    install_skill(dest=dest)

    junk = dest / "references" / "stale.md"
    junk.write_text("remove me")
    install_skill(dest=dest, force=True)

    assert not junk.exists()
    assert (dest / "SKILL.md").is_file()


def test_install_missing_bundle_raises(tmp_path, monkeypatch):
    empty = tmp_path / "empty"
    empty.mkdir()
    monkeypatch.setattr(install_mod, "_bundled_skill_dir", lambda: empty)

    with pytest.raises(FileNotFoundError):
        install_skill(dest=tmp_path / "plotnine-extra")


def test_install_excludes_checkpoints_and_pycache(tmp_path, monkeypatch):
    src = _seed_fake_skill(tmp_path / "src")
    (src / ".ipynb_checkpoints").mkdir()
    (src / ".ipynb_checkpoints" / "SKILL-checkpoint.md").write_text("nope")
    (src / "__pycache__").mkdir()
    (src / "__pycache__" / "x.pyc").write_text("nope")
    monkeypatch.setattr(install_mod, "_bundled_skill_dir", lambda: src)

    dest = install_skill(dest=tmp_path / "plotnine-extra")

    assert not (dest / ".ipynb_checkpoints").exists()
    assert not (dest / "__pycache__").exists()
    assert (dest / "references" / "foo.md").is_file()


def test_default_dests_are_under_home(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    assert _default_dest("claude") == (
        tmp_path / ".claude" / "skills" / "plotnine-extra"
    )
    assert _default_dest("codex") == (
        tmp_path / ".codex" / "skills" / "plotnine-extra"
    )


def test_install_targets_installs_both_defaults(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)

    installed = install_targets()

    assert installed == [
        ("claude", tmp_path / ".claude" / "skills" / "plotnine-extra"),
        ("codex", tmp_path / ".codex" / "skills" / "plotnine-extra"),
    ]
    assert (installed[0][1] / "SKILL.md").is_file()
    assert (installed[1][1] / "SKILL.md").is_file()


def test_install_targets_rejects_dest_with_both(tmp_path):
    with pytest.raises(ValueError, match="--dest"):
        install_targets(dest=tmp_path / "skill")


def test_install_targets_preflights_both_before_copying(tmp_path, monkeypatch):
    monkeypatch.setattr(Path, "home", lambda: tmp_path)
    codex_dest = tmp_path / ".codex" / "skills" / "plotnine-extra"
    codex_dest.mkdir(parents=True)

    with pytest.raises(FileExistsError):
        install_targets()

    assert not (tmp_path / ".claude" / "skills" / "plotnine-extra").exists()


def test_main_print_path(capsys):
    result = main(["--print-path"])

    assert result == 0
    assert capsys.readouterr().out.strip().endswith("data")
