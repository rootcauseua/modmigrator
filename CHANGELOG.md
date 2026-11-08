# Changelog

## [0.1.0] — 2026-11-08

Initial early release.

### Added
- CLI `migrator.py`: copies mod data between two `.minecraft` folders.
- Dry-run by default; files are copied only with an explicit `--yes`.
- Profiles for JourneyMap (waypoints only, or full data incl. map tiles),
  Xaero's Minimap, Xaero's World Map, JEI and REI.
- `--skip`, `--overwrite` and `--list` options; files that match several
  profiles are counted and copied once.
- Waystones documented as a special case: its data lives inside the world
  save, not in `config/`, so there is nothing to copy.
- 14 automated tests (`pytest test_migrator.py`).

### Known limitations
- Xaero's, JEI and REI paths are common-path guesses, not yet confirmed on
  real installs; JourneyMap waypoint paths are partly verified.
