# modmigrator

![version](https://img.shields.io/badge/version-0.1.0-red)
![python](https://img.shields.io/badge/python-3.10%2B-blue)
![license](https://img.shields.io/badge/license-MIT-green)
![tests](https://img.shields.io/badge/tests-14%20passing-brightgreen)

Переносить дані модів Minecraft (waypoints, закладки, конфіги) між двома
папками `.minecraft` — наприклад, зі старої версії гри на нову, або між
двома інстансами (Prism Launcher, MultiMC тощо).

Moves Minecraft mod data (waypoints, bookmarks, configs) between two
`.minecraft` folders — e.g. when upgrading Minecraft versions, or
between two instances (Prism Launcher, MultiMC, etc).

## > demo

Приклад виводу (dry-run на тестовій структурі папок) / example output
(dry-run on a sample folder structure):

```
$ python migrator.py demo out --mods journeymap_waypoints xaeros_minimap

[увага] профіль 'journeymap_waypoints' — шляхи перевірені не повністю (partly_verified), перевір знайдені файли уважно перед копіюванням.
[увага] профіль 'xaeros_minimap' — шляхи перевірені не повністю (best_guess), перевір знайдені файли уважно перед копіюванням.

=== JourneyMap — лише waypoints (мітки) (~ частково перевірений) ===
    Тільки мітки, без тайлів карти (легко, кілька КБ). Шлях journeymap/data/sp/<світ>/waypoints підтверджений логами гри та форумом FTB; для серверів (data/mp/...) структура така сама за шаблоном, але прямо не перевірена.
    Знайдено 3 файл(ів), 49.0 B
      journeymap/data/mp/play_example_net/waypoints/spawn.json
      journeymap/data/sp/MyWorld/waypoints/base.json
      journeymap/data/sp/MyWorld/waypoints/home.json

=== Xaero's Minimap (? приблизний шлях) ===
    Шлях 'XaeroWaypoints' відомий, але точна структура config може відрізнятись між версіями мода — перевір dry-run перед копіюванням.
    Знайдено 1 файл(ів), 3.0 B
      XaeroWaypoints/Multiplayer_example/waypoints.txt

Це був DRY-RUN. Нічого не скопійовано.
Щоб реально скопіювати ці 4 файл(ів), додай прапорець --yes до тієї ж команди.
```

## Статус / Status

**v0.1.0 — ранній реліз.** Найповніше підтримується JourneyMap; профілі
Xaero's, JEI та REI спираються на типові шляхи й уточнюються. Якщо профіль
нічого не знайшов — відкрий issue з виводом
`Get-ChildItem .minecraft\config -Directory`.

**v0.1.0 — early release.** JourneyMap is covered most fully; the Xaero's,
JEI and REI profiles use common paths and are being refined. If a profile
finds nothing, open an issue with the output of
`Get-ChildItem .minecraft\config -Directory`.

## Головне правило / The main rule

**Нічого не копіюється без явного підтвердження.** Запуск без `--yes`
завжди лише показує план (dry-run) — що знайдено, скільки файлів, їх
розмір. Копіювання відбувається тільки другим окремим запуском з
`--yes`.

**Nothing is copied without explicit confirmation.** Running without
`--yes` always just shows a plan (dry-run) — what was found, how many
files, their size. Copying only happens on a second, separate run with
`--yes`.

## Чому не "перенести всі моди автоматично" / Why not "migrate all mods automatically"

Кожен мод зберігає дані по-своєму: немає єдиного стандарту. Тому
інструмент працює через **профілі** — для кожного мода окремо описано,
де шукати його файли. Статуси достовірності: `partly_verified` — частину шляху підтверджено
логами гри і форумом (`journeymap/data/sp/<світ>/waypoints`), решта за
шаблоном; `best_guess` — з пам'яті, може не збігатися з твоєю версією
мода. Офіційна сторінка JourneyMap "Data Files" порожня, тож
повністю підтвердити за документацією не вдалося. Саме тому є dry-run: перш ніж
щось копіювати, ти бачиш точний список знайдених файлів.

Each mod stores its data differently — there's no shared standard.
That's why the tool works via **profiles**: each mod has its own
description of where to look. Profiles marked `best_guess` are from
memory and might not match your exact mod version — that's exactly why
dry-run exists: you see the exact file list before anything is copied.

## Встановлення / Installation

Потрібен лише Python 3.10+, без залежностей.
Needs only Python 3.10+, no dependencies.

```bash
git clone https://github.com/rootcauseua/modmigrator.git
cd modmigrator
```

## Використання / Usage

Подивитись усі доступні профілі модів:
```bash
python migrator.py --list
```

Перевірити, що буде знайдено (dry-run, нічого не копіює):
```bash
python migrator.py "C:\Users\you\AppData\Roaming\.minecraft" "C:\Users\you\AppData\Roaming\.minecraft_new" --mods journeymap_waypoints xaeros_minimap
```

Реально скопіювати (окремий запуск з `--yes`):
```bash
python migrator.py "C:\...\.minecraft" "C:\...\.minecraft_new" --mods journeymap_waypoints xaeros_minimap --yes
```

Перенести все, крім важких тайлів карти:
```bash
python migrator.py SOURCE DEST --mods all --skip xaeros_worldmap --yes
```

Перезаписати файли, що вже існують у dest:
```bash
python migrator.py SOURCE DEST --mods journeymap --yes --overwrite
```

## Підтримувані моди / Supported mods

| Профіль | Мод | Впевненість |
|---|---|---|
| `journeymap_waypoints` | JourneyMap, лише мітки (легко) | ~ partly_verified |
| `journeymap` | JourneyMap, усе разом з тайлами карти (може бути ГБ) | ~ partly_verified |
| `xaeros_minimap` | Xaero's Minimap | ? best_guess |
| `xaeros_worldmap` | Xaero's World Map | ? best_guess |
| `jei` | JEI (Just Enough Items) | ? best_guess |
| `rei` | REI (Roughly Enough Items) | ? best_guess |

Докладніше про кожен — `python migrator.py --list`.

## Waystones — особливий випадок / Waystones — a special case

Waystones не має окремого профілю, бо його дані лежать не в config/, а
прямо всередині сейву світу (`saves/<world>/data/waystones.dat`). Якщо
переносиш той самий сейв на нову версію — вейстоуни вже там, копіювати
нічого не треба. Деталі — `python migrator.py --list`.

## Як додати новий мод / How to add a new mod

Відкрий `profiles.py`, додай новий запис у словник `PROFILES`:

```python
"my_mod": ModProfile(
    key="my_mod",
    display_name="My Mod",
    patterns=["config/my_mod/**/*"],
    confidence="best_guess",
    note="Опиши, що саме це за дані.",
),
```

Патерни — відносно кореня `.minecraft`, у форматі Python `pathlib`
glob (підтримує `**` для рекурсивного пошуку).

## Тести / Tests

```bash
pip install pytest
pytest test_migrator.py -v
```

14 тестів: пошук файлів, dry-run, копіювання зі збереженням структури,
захист від перезапису, `--skip`, відсутність подвійного підрахунку,
обробка помилок. / 14 tests: file discovery, dry-run, copying with
structure preserved, overwrite protection, `--skip`, no double counting,
error handling.

## Відомі обмеження / Known limitations

- Профілі `best_guess` писались з пам'яті без доступу до реальних
  інстансів модів, а `partly_verified` підтверджені лише частково —
  завжди перевіряй dry-run перед `--yes`.
- Не зливає конфлікти (наприклад, два різні списки waypoints з однаковою
  назвою файлу) — просто пропускає існуючі файли, якщо не передано
  `--overwrite`.
- Не розуміє формати даних модів зсередини — лише копіює файли як є,
  не конвертує між несумісними версіями формату самого мода.

## License

MIT
