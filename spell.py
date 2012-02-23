"""
Spells and Abilities.
Maybe more combat too.
"""

from __future__ import print_function, division, unicode_literals

# Constants for tuning combat...
# Hit Chance
HIT_BASE = 0.5
HIT_BONUS = 0.9
# Base Damage and number of points difference needed for a bonus point of damage
MIN_DMG_BASE = 4
MIN_DMG_INTERVAL = 6
MAX_DMG_BASE = 6
MAX_DMG_INTERVAL = 4
# Critical (2x Damage) Chance
CRIT_BASE = 0.05
CRIT_BONUS = 0.01


def chance_to_hit(accuracy, evasion):
    """
    Calculate chance to hit, based on attacker's accuracy and defender's evasion.

    For HIT_BASE = 0.5, and HIT_BONUS = 0.9...
    If evasion is the same as accuracy, hit chance is 50%.
    For each point evasion is higher than accuracy,
        chance to hit is reduced by about 5%, with diminishing returns as it approaches 0%
    For each point evasion is lower than accuracy,
        chance to hit is increased by about 5%, with diminishing returns as it approaches 100%
    
    A handy table...
    for (accuracy - evasion):
        -20:     6%
        -10:    17%
         -5:    29%
         -2:    40%
         -1:    45%
          0:    50%
         +1:    55%
         +2:    59%
         +5:    70%
        +10:    82%
        +20:    93%
    """
    advantage = accuracy - evasion
    if advantage < 0:
        return HIT_BASE * (HIT_BONUS ** (-advantage))
    elif advantage > 0:
        return 1.0 - ((1.0 - HIT_BASE) * (HIT_BONUS ** (advantage)))
    else:
        return HIT_BASE

def attack_damage(level, attack, defense):
    """
    Calculate successful attack damage.

    This one's messier.
    Advantage = Attack - Defense
    Base damage is 4-6, Base crit chance is 5%.
    +1 to Min damage for every 6 points advantage.
    +1 to Max damage for every 4 points advantage.
    +1% to Crit chance for every point.

    +1 to Min/Max damage for every 2 levels.
    This one is not based on a comparison.
    It just means that damage amounts will steadily increase as levels do.

    For negative advantage, all damage values are capped at 1.
    Negative crit chance becomes -2x glance chance.

    Critical Hit means double damage values.
    Glancing Hit means half damage values.
    """
    advantage = attack - defense
    crit_chance = CRIT_BASE + CRIT_BONUS * advantage
    if crit_chance < 0.0:
        glance_chance = -2.0 * crit_chance
        crit_chance = 0.0
    else:
        glance_chance = 0.0

    min_damage = MIN_DMG_BASE + ((advantage + (MIN_DMG_INTERVAL // 2)) // MIN_DMG_INTERVAL) + ((level-1) // 2)
    max_damage = MAX_DMG_BASE + (advantage // MAX_DMG_INTERVAL) + (level // 2)

    if min_damage < 1:
        max_damage -= (1 - min_damage)
        min_damage = 1
    if max_damage < 1:
        max_damage = 1

    # TODO: If crit, double damage. Halve damage on glance.
    return (min_damage, max_damage, crit_chance, glance_chance)

class Spell(object):
    """
    A generic Spell/Ability.

    Spells have:
        MP Cost (0 for purely physical abilities)
        A List of Effects (2-tuples of effect types with parameters)
        TODO: Conditional effects
            e.g. a Drain spell should not add more HP to the caster than the defender has.
    """
    def __init__(self, name, cost, effects):
        self.name = name
        self.cost = cost
        self.effects = effects

    def cast_spell(self, caster, target, args):
        """
        Apply this spell to the target with the given args.

        TODO: Raise exception if insufficient MP, or for invalid target.
        """
        # TODO: implement me
        pass

    def __repr__(self):
        if self.cost > 0:
            return '%s (%dMP)' % (self.name, self.cost)
        else:
            return self.name


# vim: sw=4 ts=4 expandtab
