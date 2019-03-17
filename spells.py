"""Master spell list:
    Nature Magic:
        1: Lesser Mend, Quicksand, Ward
        2: Regen, Sleep, Lesser Cure
        3: Healing Wave, Entangle, Fury
        4: Mend, Sandstorm, Cure
        5: Mass Regen, Raise, Mass Ward
        6: Greater Healing Wave, Tornado, Panacea
        7: Greater Mend, Wild Fury
        8: Miracle
    Elemental Magic:
        1: Freeze, Flare, Bolt
        2: Quake, Wind Blast, Incinerate
        3: Mass Freeze, Flamewave, Chain Lightning
        4: Ice Blast, Fireball, Thunderstrike
        5: Greater Quake, Tsunami, Tailwind
        6: Blizzard,
"""

# The dictionary of all spells in the game
spells_dict = {
    'lessermend': {
        'name': 'Lesser Mend',  # The name of the spell.
        'category': 'Nature',  # Which school of magic the spell belongs to.
        'flags': ('heal', 'single'),  # Flags describing how the spell behaves.
        'allowed_jobs': ('Mage', 'Green Wizard', 'Lifeweaver', 'Storm Shaman'),  # Classes that can slot this spell.
        'rank': 1,  # Spell slots are ranked 1-7, with 7 being the most powerful spells.
        'potency': 30  # Potency coefficient for spells.
    }
}


def spelldamage(primarystat: int, level: int, potency: int) -> int:
    """Calculate direct damage and direct healing for spells based on potency. Damage is calculated based on the
    following formula, where L is character level, S is the primary stat used by the relevant school of magic, and
    P is the spell's potency rating:
            X = P + P((L^2)/2)
            output = X + X(S/100)"""

    f1 = level ** 2
    f1 = int(f1 / 2)
    f1 *= potency
    f1 += potency
    f2 = float(primarystat / 100.0)
    output = f1 + (f1 * f2)
    return int(output)
