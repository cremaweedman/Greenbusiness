MAX_LEVEL = 20
SKILL_BRANCHES = ("botany", "commerce", "operations")


class UnlockDefinition:
    __slots__ = ("key", "kind", "label", "level")

    def __init__(self, key: str, kind: str, level: int, label: str) -> None:
        self.key = key
        self.kind = kind
        self.level = level
        self.label = label


def xp_cost_for_level(level: int) -> int:
    if level < 1:
        raise ValueError("level must be >= 1")
    return round(100 * (level**1.45))


def cumulative_xp_for_level(level: int) -> int:
    if level <= 1:
        return 0
    capped = min(level, MAX_LEVEL)
    return sum(xp_cost_for_level(current) for current in range(1, capped))


def level_for_xp(xp: int) -> int:
    level = 1
    while level < MAX_LEVEL and xp >= cumulative_xp_for_level(level + 1):
        level += 1
    return level


def awarded_skill_points(level: int) -> int:
    return max(0, level - 1)


UNLOCKS = (
    UnlockDefinition("contracts-standard", "system", 1, "Standard contracts"),
    UnlockDefinition("ember-leaf", "variety", 1, "Ember Leaf"),
    UnlockDefinition("moon-sprout", "variety", 1, "Moon Sprout"),
    UnlockDefinition("efficient-racks-1", "upgrade", 1, "Efficient Racks I"),
    UnlockDefinition("contracts-premium", "system", 3, "Premium contracts"),
    UnlockDefinition("efficient-racks-2", "upgrade", 4, "Efficient Racks II"),
    UnlockDefinition("specialized-contracts", "system", 5, "Specialized contracts"),
    UnlockDefinition("efficient-racks-3", "upgrade", 8, "Efficient Racks III"),
)


def unlocked_keys(level: int) -> list[str]:
    return [unlock.key for unlock in UNLOCKS if unlock.level <= level]


def next_level_xp(level: int) -> int | None:
    if level >= MAX_LEVEL:
        return None
    return cumulative_xp_for_level(level + 1)
