"""
Basic entity class and its subclasses.
"""

# FUTURE DECLARATIONS :D
# These are all things that have changed in Python 3.  (Generally major improvements that would break old code)
# Rather than breaking everything at once, Python 2 allows you to keep using crusty, old syntax.
# Future declarations activate these new features, and are ignored in newer Pythons where the new stuff is standard.
# 'print_function' changes 'print' from a statement to a function.
#   Use like this: print('Some text')
# 'division' makes division less surprising.
#   Use '//' for integer division. Use '/' if you want a float result.
#   Without this, '/' gives different results for '3 / 2' (1) and '3 / 2.' (1.5).
# 'unicode_literals' makes all strings Unicode-capable, rather than byte strings.
#   If you do need a literal string of bytes in your code (e.g. for file or network I/O), use b'string'.

# TL;DR --> Write code that runs in both Python 2.6+ (practically every Ubuntu ever) and 3.x
from __future__ import print_function, division, unicode_literals

from random import randint

def xp_for_level(level):
    """
    Calculate XP needed for level.

    50 * level * (level - 1)

    1: 0xp
    2: 100xp    +100xp
    3: 300xp    +200xp
    4: 600xp    +300xp
        ...
    """
    return 50 * level * (level - 1)

# Dictionary mapping attributes to their display names
# TODO: Move this into a central location for keeping strings
#   This allows for easy localization (not that that's a likely goal here, just saying)
attr_names = {
        'maxhp':    'Max HP',
        'maxmp':    'Max MP',
        'atk':      'Attack',
        'def':      'Defense',
        'acc':      'Accuracy',
        'eva':      'Evasion',
        'matk':     'Magic Attack',
        'mdef':     'Magic Defense',
        'macc':     'Magic Accuracy',
        'meva':     'Magic Evasion',
        }

class Job(object):
    """
    A generic Job type.

    Attribute types:
        maxhp           - Damage-taking capability
        maxmp           - Spell-casting capability
        atk             - Bonus to physical damage
        def             - Physical damage reduction
        acc             - Chance to do physical damage
        eva             - Chance to avoid physical damage
        matk            - Bonus to magical damage
        mdef            - Magical damage resistance
        macc            - Chance to do magical damage
        meva            - Chance to avoid magical damage

    attr_ranges should be a dictionary that maps stat names to a 4-tuple containing:
        min, max starting values
        min, max increase per level

    You only need to give values for attributes if they differ from the default.

    To create an Entity with a job, call the job's create_entity method.
    """
    def __init__(self, name, attr_ranges=None, magic_resists=None):
        self.name = name
        # Default attribute ranges (min_base, max_base, min_per_level, max_per_level)
        self.attr_ranges = {
                'maxhp':    (17, 23, 1, 3),
                'maxmp':    (17, 23, 1, 3),
                'atk':      (8, 12, 0, 2),
                'def':      (8, 12, 0, 2),
                'acc':      (8, 12, 0, 2),
                'eva':      (8, 12, 0, 2),
                'matk':     (8, 12, 0, 2),
                'mdef':     (8, 12, 0, 2),
                'macc':     (8, 12, 0, 2),
                'meva':     (8, 12, 0, 2),
                }
        if attr_ranges is not None:
            self.attr_ranges.update(attr_ranges)

        self.magic_resists = {
                'arcane': 0,
                'fire': 0,
                'frost': 0,
                'nature': 0,
                }
        if magic_resists is not None:
            self.magic_resists.update(magic_resists)
        
        self.max_level = 60

    def create_entity(self, unique_name=None):
        """
        Create a new Entity based on these parameters.
        """
        return Entity(job=self, name=unique_name)

    def __repr__(self):
        return self.name

class Entity(object):
    """
    Base entity class.

    Every entity has:
        Job         - Determines base stats and abilities
        Name        - (Optional) Unique display name
        Level       - These do some hidden magic to keep everything consistent, and can't be reduced
            level   - Experience Level
            xp      - Experience Points
        Attributes  - Randomly generated static attributes (unique to this entity)
            all others mentioned earlier, plus
            gear    - TODO: Semi-permanent status effects
                      Map from (body location -> item)
        Status      - Volatile status
            hp      - Current HP
            mp      - Current MP
            effects - TODO: Temporary status effects
                      List of tuples containing effect type, magnitude, and remaining duration
    """
    def __init__(self, job, name=None):
        self.job = job
        self.name = name

        # Basic stats
        self._level = 1
        self._xp = 0
        self._hp = 0
        self._mp = 0

        # Generate starting attributes from job
        self.attributes = {attr: randint(bounds[0], bounds[1]) for attr, bounds in self.job.attr_ranges.items()}
        
        # Initialize current HP and MP to their respective maximums
        self.restore_health()

        # Inventory and Equipment
        # TODO: Might add some job-based starting items
        # TODO: Keep inventory tracked by Party?
        self.equipment = {}

    def __repr__(self):
        """
        Give this entity's name (if it has one) and Job.
        If it has no name (name is None), give just its Job.
        """
        if self.name:
            return '%s <%s>' % (self.name, self.job)
        else:
            return '%s' % (self.job)

    def set_xp(self, xp):
        """
        Set XP, and level up if necessary.

        Raises ValueError when trying to reduce XP.
        TODO: Allow reduction of XP if the current Level would remain valid. 
        TODO: Raise an exception derived from ValueError
        """
        if xp < self._xp:
            raise ValueError("Cannot decrease XP.")

        # Increase XP, and increase level as appropriate
        self._xp = xp
        while xp >= xp_for_level(self._level + 1):
            self._level += 1
            self.advance_level()

    xp = property(lambda self: self._xp, set_xp, doc="""
    Experience points.
    
    May only increase, attempting to decrease raises ValueError.
    Syncronized with level.
    If increasing this causes the level to increase, stat improvements are awarded automatically.
    """)

    def set_level(self, level):
        """
        Set Level, and increase XP if necessary.

        Does nothing when setting Level to the current Level.
        Raises ValueError when trying to reduce Level.
        TODO: Raise an exception derived from ValueError
        TODO: On level up, instead of applying the effects instantly,
            could simply increase some counter of level-ups "available"
            This would let the user interface know what's up.
        TODO: Limit level to job.max_level
        """
        if level < self._level:
            raise ValueError("Cannot decrease Level.")
        elif level == self._level:
            # Do nothing (Don't reduce XP to level threshold)
            return

        # Increase XP to new level's threshold
        self._xp = xp_for_level(level)

        # Could have simply set _level to the new value, but this might allow us to do level-specific behavior in advance_level().
        for _ in range(level - self._level):
            self._level += 1
            self.advance_level()

    level = property(lambda self: self._level, set_level, doc="""
    Experience level.
    
    May only increase, attempting to decrease raises ValueError.
    Syncronized with xp.
    When level is increased, stat improvements are awarded automatically.
    """)

    def set_alive(self, alive):
        """
        If setting alive to False, reduce HP to 0.
        If setting to True and HP is <= 0, raise to 1.
        """
        if not alive:
            self._hp = 0
        elif self._hp <= 0:
            self._hp = 1

    alive = property(lambda self: self._hp > 0, set_alive, doc="""
    True if HP > 0, False otherwise.

    Setting this to False reduces HP to 0.
    When setting to True, if HP is <= 0, sets HP to 1.
    """)

    def set_hp(self, hp):
        """
        Sets HP, while keeping it clamped between 0 and MaxHP.
        """
        self._hp = max(0, min(self.attributes['maxhp'], self._hp))

    hp = property(lambda self: self._hp, set_hp, doc="""
    Hit points (HP).

    An entity loses HP when taking damage, and is considered dead when at 0 HP.
    HP is clamped between 0 and MaxHP.
    """)

    def set_mp(self, mp):
        """
        Sets MP, while keeping it clamped between 0 and MaxMP.
        """
        self._mp = max(0, min(self.attributes['maxmp'], self._mp))

    mp = property(lambda self: self._mp, set_mp, doc="""
    Magic/Mana points (MP).

    MP may be spent to cast spells.
    MP is clamped between 0 and MaxMP.
    """)

    # Some code de-duplication...
    def advance_level(self):
        """
        Increase attributes as part of the level-up process.
        """
        # Generate per-level increases from job
        
        if self.level is self.job.max_level:
            print("%s is already max level!" % (self.name))
            return
        else:
            awards = {attr: randint(bounds[2], bounds[3]) for attr, bounds in self.job.attr_ranges.items()}
            for attr, value in awards.items():
                self.attributes[attr] += value
            self._hp += awards['maxhp']
            self._mp += awards['maxmp']
            self._level += 1

    def restore_health(self):
        """
        Set HP and MP to their respective maximums
        """
        self._hp = self.attributes['maxhp']
        self._mp = self.attributes['maxmp']

    def print_status(self, width=50):
        """
        Print detailed information about this Entity to stdout.
        """
        # Print separator
        print('='*width)
        # Print name and whatever
        print('%s' % (self))
        print(' Level: %d (%dXP), To next: %dXP' % (self.level, self.xp, xp_for_level(self.level+1)-self.xp))
        print(' HP: %d / %d, MP: %d / %d' % (self.hp, self.attributes['maxhp'], self.hp, self.attributes['maxhp']))
        print('Attributes')
        # List Attributes
        # This feels hackish, but it's only temporary (ideally, this will all be formatted by something else)
        # Also, Meet the Generator Expression.
        #   It works just like a list comprehension (same syntax, but with []'s),
        #   with the added bonus of not generating the whole thing all at once.
        #   Items are generated as needed, which is really nice for long lists.
        for line in (' %16s: %3d  %16s: %3d' % (attr_names[attr], self.attributes[attr], attr_names['m'+attr], self.attributes['m'+attr]) for attr in ['atk', 'def', 'acc', 'eva']):
            print(line)
        # TODO: List Resists
        # TODO: List Abilities/Spells
        # TODO: List Equipment
        # TODO: List Status Effects
        # Print separator
        print('='*width)


class Party(object):
    """
    A group of allied Entity objects.

    A Party shares its inventory.
    TODO: This may either mean that all items are tracked by Party, or that Entities still track items, but Party sums them transparently.
    A Party is considered defeated when all its members are dead.

    TODO: May make this a subclass of list.
    """
    def __init__(self, members=None):
        if members is not None:
            self.members = members

    def __repr__(self):
        return str(self.members)

# vim: sw=4 ts=4 expandtab
