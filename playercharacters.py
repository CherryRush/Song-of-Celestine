import os
import pygame
import mirrorgame

from pygame import *


"""The following Dictionary contains data used to build characters based on their classes. The following
character classes are planned:
Anna:
        Mage
        TODO: Brown Wizard (Hybrid Damage)
        TODO: Green Wizard (Healer / Magic Damage / Support)
        TODO: Crystal Knight (Tank)
        TODO: Blue Wizard (Support)
        TODO: Black Wizard(Magic Damage)
Clara:
        TODO: Bard
        TODO: Lifeweaver (Healer / Support)
        TODO: Bladedancer (Melee Damage)
        TODO: Siren (Magic Damage / Support)
        TODO: Skald (Tank)
Carter:
        TODO: Rogue
        TODO: Gunslinger (Ranged Damage)
        TODO: Ninja (Melee Damage)
        TODO: Fencer (Tank)
        TODO: Artificer (Healer / Hybrid Damage)
Wilhelm:
        TODO: Fighter
        TODO: Guardian (Tank)
        TODO: Slayer (Melee Damage)
        TODO: Praetorian (Ranged Damage)
        TODO: Storm Shaman (Healer / Hybrid Damage)"""

jobs_dict = {
    # The Mage, Anna's base class. Low HP, STR, CON, and LUCK; Med WILL, AGI, and INT. High MP.
    #   "Jack of all Trades" caster with basic Nature, Elemental, and Crystal spells.
    'Mage': {
        'hp_growth': 1.5,  # The HP growth coefficient. Multiply by 20 to get base health at level 1.
        'mp_growth': 3.5,  # The MP growth coefficient. Multiply by 20 to get base mana at level 1.
        'str_growth': 1.0,  # The STR growth coefficient. Multiply by 10 to get base STR at level 1.
        'agi_growth': 2.2,  # The AGI growth coefficient. Multiply by 10 to get base AGI at level 1.
        'con_growth': 1.5,  # The CON growth coefficient. Multiply by 10 to get base CON at level 1.
        'int_growth': 3.0,  # The INT growth coefficient. Multiply by 10 to get base INT at level 1.
        'will_growth': 2.5,  # The WILL growth coefficient. Multiply by 10 to get base WILL at level 1.
        'luck_growth': 1.3,  # The LUCK growth coefficient. Multiply by 10 to get base LUCK at level 1.

        # Equippable weapons and armor.
        'equipset': ('dagger', 'lit_blade', 'wand', 'staff', 'focus', 'lit_armor'),

        # Learnsets for passives and physical abilities. Spells and songs are learned by buying them
        #   from magic shops and slotting them in a character's spellbook.
        'passive_learnset': {
            1: 'magicrank1',
            6: 'magicrank2',
            12: 'magicrank3',
        },
        'ability_learnset': {

        },

        # Available Heroic Abilities. As a basic class, Mage has only two; specialist classes have three.
        'heroics': ['shockwave', 'hidden_potential'],

        # Starting gear equipped to main-hand, off-hand, armor, accessory1, and accessory2 when character
        #   is first recruited.
        'start_gear': ['apprenticestaff', None, 'clothes', None, None],

        # Starting spells in spellbook when character is first recruited.
        'start_spells': {
            1: ['lessermend', 'freeze', 'crystalshard']
        }
    },
}