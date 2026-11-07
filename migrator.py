#!/usr/bin/env python3
"""
migrator.py — переносить дані модів (waypoints, закладки, конфіги) між
двома папками .minecraft (наприклад, старою та новою версією гри).

НІЧОГО не копіюється без підтвердження: спочатку --dry-run (або просто
запуск без --yes) показує, що саме знайдено і буде скопійовано.

Usage:
    python migrator.py SOURCE DEST --mods journeymap xaeros_minimap
    python migrator.py SOURCE DEST --mods all --yes
    python migrator.py SOURCE DEST --list

Author: rootcause
License: MIT
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

from profiles import PROFILES, SPECIAL_NOTES


def find_matches(source_root: Path, patterns: list[str]) -> list[Path]:
    """Повертає всі файли (не папки), що збігаються з хоч одним патерном."""
    matches: set[Path] = set()
    for pattern in patterns:
        for p in source_root.glob(pattern):
            if p.is_file():
                matches.add(p)
    return sorted(matches)


def human_size(num_bytes: int) -> str:
    size = float(num_bytes)
    for unit in ("B", "KB", "MB", "GB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} TB"


def plan_for_mod(source_root: Path, mod_key: str) -> tuple[list[Path], int]:
    profile = PROFILES[mod_key]
    files = find_matches(source_root, profile.patterns)
    total_size = sum(f.stat().st_size for f in files)
    return files, total_size


def print_plan(source_root: Path, mod_keys: list[str]) -> dict[str, list[Path]]:
    plan: dict[str, list[Path]] = {}
    print()
    for key in mod_keys:
        profile = PROFILES[key]
        files, total_size = plan_for_mod(source_root, key)
        plan[key] = files
        confidence_tag = {
            "confirmed": "✓ перевірений шлях",
            "partly_verified": "~ частково перевірений",
        }.get(profile.confidence, "? приблизний шлях")
        print(f"=== {profile.display_name} ({confidence_tag}) ===")
        if profile.note:
            print(f"    {profile.note}")
        if not files:
            print("    Нічого не знайдено за відомими шляхами.")
        else:
            print(f"    Знайдено {len(files)} файл(ів), {human_size(total_size)}")
            for f in files[:10]:
                print(f"      {f.relative_to(source_root)}")
            if len(files) > 10:
                print(f"      ... і ще {len(files) - 10}")
        print()
    return plan


def copy_plan(plan: dict[str, list[Path]], source_root: Path, dest_root: Path,
               overwrite: bool) -> None:
    copied = 0
    skipped = 0
    seen: set[Path] = set()  # один файл може потрапити в кілька профілів
    for key, files in plan.items():
        for src in files:
            if src in seen:
                continue
            seen.add(src)
            rel = src.relative_to(source_root)
            dst = dest_root / rel
            if dst.exists() and not overwrite:
                skipped += 1
                continue
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
    print(f"\nГотово: скопійовано {copied} файл(ів)"
          + (f", пропущено {skipped} (вже існують — передай --overwrite щоб перезаписати)"
             if skipped else "") + ".")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Переносить дані модів Minecraft між двома .minecraft папками.")
    parser.add_argument("source", nargs="?", type=Path,
                         help="Шлях до старої .minecraft (звідки переносимо)")
    parser.add_argument("dest", nargs="?", type=Path,
                         help="Шлях до нової .minecraft (куди переносимо)")
    parser.add_argument("--mods", nargs="+", default=["all"],
                         help="Які моди переносити: ключі зі списку (--list) або 'all'")
    parser.add_argument("--skip", nargs="*", default=[],
                         help="Виключити конкретні моди навіть якщо вказано 'all'")
    parser.add_argument("--yes", action="store_true",
                         help="Пропустити підтвердження і одразу копіювати "
                              "(БЕЗ ЦЬОГО ФЛАГУ нічого не копіюється — лише показ плану)")
    parser.add_argument("--overwrite", action="store_true",
                         help="Перезаписувати файли, що вже існують у dest")
    parser.add_argument("--list", action="store_true",
                         help="Показати всі доступні профілі модів і вийти")
    args = parser.parse_args(argv)

    if args.list:
        print("Доступні профілі модів:\n")
        for key, profile in PROFILES.items():
            print(f"  {key:22} {profile.display_name} [{profile.confidence}]")
        print("\nОсобливі випадки (не мають окремого профілю):")
        for key, note in SPECIAL_NOTES.items():
            print(f"\n  {key}:\n    {note}")
        return 0

    if args.source is None or args.dest is None:
        parser.error("source і dest обов'язкові (крім --list)")

    source_root: Path = args.source
    dest_root: Path = args.dest

    if not source_root.is_dir():
        print(f"Помилка: папка-джерело не знайдена: {source_root}", file=sys.stderr)
        return 1

    mod_keys = list(PROFILES.keys()) if "all" in args.mods else args.mods
    unknown = [k for k in mod_keys if k not in PROFILES]
    if unknown:
        print(f"Помилка: невідомі моди: {', '.join(unknown)}. "
              f"Використай --list щоб побачити доступні.", file=sys.stderr)
        return 1
    mod_keys = [k for k in mod_keys if k not in args.skip]

    for key in mod_keys:
        if PROFILES[key].confidence != "confirmed":
            print(f"[увага] профіль '{key}' — шляхи перевірені не повністю "
                  f"({PROFILES[key].confidence}), перевір знайдені файли "
                  f"уважно перед копіюванням.")

    plan = print_plan(source_root, mod_keys)

    total_files = len({f for files in plan.values() for f in files})
    if total_files == 0:
        print("Нічого переносити — жоден профіль нічого не знайшов.")
        return 0

    if not args.yes:
        print(f"Це був DRY-RUN. Нічого не скопійовано.")
        print(f"Щоб реально скопіювати ці {total_files} файл(ів), "
              f"додай прапорець --yes до тієї ж команди.")
        return 0

    dest_root.mkdir(parents=True, exist_ok=True)
    copy_plan(plan, source_root, dest_root, args.overwrite)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
