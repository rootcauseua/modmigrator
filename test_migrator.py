"""Тести для modmigrator. Запуск: pytest test_migrator.py -v"""

from pathlib import Path

import pytest

import migrator
from profiles import PROFILES


def make_tree(root: Path) -> None:
    """Тестова структура .minecraft з файлами кількох модів."""
    files = {
        "journeymap/data/sp/MyWorld/waypoints/home.json": '{"name": "home"}',
        "journeymap/data/sp/MyWorld/waypoints/base.json": '{"name": "base"}',
        "journeymap/data/mp/play_example_net/waypoints/spawn.json": '{"name": "spawn"}',
        "journeymap/data/sp/MyWorld/DIM0/tile.png": "tile-bytes",
        "config/journeymap/journeymap.core.config": "cfg",
        "XaeroWaypoints/Multiplayer_example/waypoints.txt": "wp",
        "config/jei/jei-client.ini": "jei",
        "saves/MyWorld/data/waystones.dat": "not-a-config-file",
    }
    for rel, content in files.items():
        p = root / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")


@pytest.fixture
def src(tmp_path: Path) -> Path:
    root = tmp_path / "src"
    make_tree(root)
    return root


# --- пошук файлів / file discovery ---

def test_waypoints_profile_finds_sp_and_mp(src):
    files, _ = migrator.plan_for_mod(src, "journeymap_waypoints")
    names = {f.name for f in files}
    assert names == {"home.json", "base.json", "spawn.json"}


def test_waypoints_profile_excludes_map_tiles(src):
    files, _ = migrator.plan_for_mod(src, "journeymap_waypoints")
    assert all("DIM0" not in str(f) for f in files)


def test_full_journeymap_profile_includes_tiles_and_config(src):
    files, _ = migrator.plan_for_mod(src, "journeymap")
    names = {f.name for f in files}
    assert "tile.png" in names
    assert "journeymap.core.config" in names


def test_waystones_world_data_is_never_matched(src):
    for key in PROFILES:
        files, _ = migrator.plan_for_mod(src, key)
        assert all("waystones" not in f.name for f in files)


# --- dry-run і копіювання / dry-run and copying ---

def test_dry_run_copies_nothing(src, tmp_path):
    dst = tmp_path / "dst"
    code = migrator.main([str(src), str(dst), "--mods", "journeymap_waypoints"])
    assert code == 0
    assert not dst.exists()


def test_yes_copies_files_preserving_structure(src, tmp_path):
    dst = tmp_path / "dst"
    code = migrator.main([str(src), str(dst), "--mods", "journeymap_waypoints", "--yes"])
    assert code == 0
    assert (dst / "journeymap/data/sp/MyWorld/waypoints/home.json").read_text() == '{"name": "home"}'
    assert (dst / "journeymap/data/mp/play_example_net/waypoints/spawn.json").exists()


def test_source_files_are_untouched(src, tmp_path):
    before = {p: p.read_text() for p in src.rglob("*") if p.is_file()}
    migrator.main([str(src), str(tmp_path / "dst"), "--mods", "all", "--yes"])
    after = {p: p.read_text() for p in src.rglob("*") if p.is_file()}
    assert before == after


def test_existing_files_not_overwritten_by_default(src, tmp_path):
    dst = tmp_path / "dst"
    target = dst / "journeymap/data/sp/MyWorld/waypoints/home.json"
    target.parent.mkdir(parents=True)
    target.write_text("DO-NOT-TOUCH")
    migrator.main([str(src), str(dst), "--mods", "journeymap_waypoints", "--yes"])
    assert target.read_text() == "DO-NOT-TOUCH"


def test_overwrite_flag_replaces_existing(src, tmp_path):
    dst = tmp_path / "dst"
    target = dst / "journeymap/data/sp/MyWorld/waypoints/home.json"
    target.parent.mkdir(parents=True)
    target.write_text("OLD")
    migrator.main([str(src), str(dst), "--mods", "journeymap_waypoints", "--yes", "--overwrite"])
    assert target.read_text() == '{"name": "home"}'


def test_skip_excludes_a_mod(src, tmp_path):
    dst = tmp_path / "dst"
    migrator.main([str(src), str(dst), "--mods", "all", "--skip", "jei", "--yes"])
    assert not (dst / "config/jei").exists()
    assert (dst / "XaeroWaypoints").exists()


def test_overlapping_profiles_are_counted_once(src, tmp_path, capsys):
    migrator.main([str(src), str(tmp_path / "dst"), "--mods", "journeymap_waypoints", "journeymap"])
    out = capsys.readouterr().out
    # 3 waypoints + 1 tile + 1 config = 5 унікальних файлів, не 8
    assert "ці 5 файл" in out


# --- помилки / errors ---

def test_unknown_mod_returns_error(src, tmp_path):
    assert migrator.main([str(src), str(tmp_path / "dst"), "--mods", "nope"]) == 1


def test_missing_source_returns_error(tmp_path):
    assert migrator.main([str(tmp_path / "missing"), str(tmp_path / "dst")]) == 1


def test_list_flag_prints_profiles_and_waystones_note(capsys):
    assert migrator.main(["--list"]) == 0
    out = capsys.readouterr().out
    assert "journeymap_waypoints" in out
    assert "waystones" in out.lower()
