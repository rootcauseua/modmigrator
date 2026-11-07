"""
profiles.py — опис того, де кожен мод зберігає дані, які варто
переносити між версіями/інстансами Minecraft.

Кожен профіль має рівень впевненості (confidence):
  "partly_verified" — частина шляхів підтверджена логами гри/форумами,
                      решта за шаблоном, не перевірена
  "best_guess"      — з пам'яті, може відрізнятись залежно від версії мода;
                 інструмент покаже знайдене і попросить підтвердження
                 перед копіюванням, саме через цю невизначеність.

profiles.py — describes where each mod stores the data worth migrating
between Minecraft versions/instances.

Each profile has a confidence level (see above) — "best_guess" entries
may not match your exact mod version, which is exactly why the tool
always shows what it found and asks for confirmation before copying
anything.
"""

from dataclasses import dataclass, field


@dataclass
class ModProfile:
    key: str
    display_name: str
    # Glob-патерни відносно кореня .minecraft (регістр має значення на Linux/Mac)
    # Glob patterns relative to the .minecraft root
    patterns: list[str]
    confidence: str  # "confirmed" | "best_guess"
    note: str = ""


PROFILES: dict[str, ModProfile] = {
    "journeymap_waypoints": ModProfile(
        key="journeymap_waypoints",
        display_name="JourneyMap — лише waypoints (мітки)",
        patterns=[
            "journeymap/data/*/*/waypoints/**/*",
        ],
        confidence="partly_verified",
        note="Тільки мітки, без тайлів карти (легко, кілька КБ). Шлях "
             "journeymap/data/sp/<світ>/waypoints підтверджений логами гри та "
             "форумом FTB; для серверів (data/mp/...) структура така сама за "
             "шаблоном, але прямо не перевірена.",
    ),
    "journeymap": ModProfile(
        key="journeymap",
        display_name="JourneyMap — усе (мітки + тайли карти + конфіг)",
        patterns=[
            "journeymap/data/**/*",
            "journeymap/waypoints/**/*",  # старі версії мода / older mod versions
            "config/journeymap/**/*",
        ],
        confidence="partly_verified",
        note="УВАГА: journeymap/data містить і тайли карти (папки DIM0, DIM144...), "
             "це може бути гігабайти. Якщо потрібні лише мітки — бери "
             "journeymap_waypoints. Шляхи journeymap/waypoints (старі версії) "
             "і config/journeymap не перевірені.",
    ),
    "xaeros_minimap": ModProfile(
        key="xaeros_minimap",
        display_name="Xaero's Minimap",
        patterns=[
            "XaeroWaypoints/**/*",
            "config/xaerominimap/**/*",
        ],
        confidence="best_guess",
        note="Шлях 'XaeroWaypoints' відомий, але точна структура config "
             "може відрізнятись між версіями мода — перевір dry-run перед копіюванням.",
    ),
    "xaeros_worldmap": ModProfile(
        key="xaeros_worldmap",
        display_name="Xaero's World Map",
        patterns=[
            "XaeroWorldMap/**/*",
        ],
        confidence="best_guess",
        note="Кешовані тайли карти — великий об'єм, можеш виключити якщо "
             "не критично (--skip xaeros_worldmap).",
    ),
    "jei": ModProfile(
        key="jei",
        display_name="JEI (Just Enough Items)",
        patterns=[
            "config/jei/**/*",
        ],
        confidence="best_guess",
        note="Закладки (bookmarks) та налаштування пошуку.",
    ),
    "rei": ModProfile(
        key="rei",
        display_name="REI (Roughly Enough Items)",
        patterns=[
            "config/rei/**/*",
            "config/reisearch/**/*",
        ],
        confidence="best_guess",
        note="Точний шлях залежить від версії REI — якщо dry-run нічого "
             "не знайде, перевір назву папки вручну в config/.",
    ),
}


SPECIAL_NOTES = {
    "waystones": (
        "Waystones НЕ має окремих клієнтських файлів для переносу — "
        "дані (де стоять вейстоуни) зберігаються прямо в сейві світу "
        "(saves/<world>/data/waystones.dat), а не в config/. "
        "Якщо переносиш той самий сейв на нову версію — вейстоуни вже "
        "там, нічого копіювати не треба. Якщо хочеш перенести вейстоуни "
        "НА ІНШИЙ сейв — це вже редагування world save, інший інструмент "
        "і інший рівень ризику (можна пошкодити світ)."
    ),
}
