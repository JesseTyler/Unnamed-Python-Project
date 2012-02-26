#   Graveyard of old class/function definitions for possible reference in order to free room in main.py

#
#   Entity Class
#

class Entity:
        #Define spells by: class type(Entity)  ..  type_1 = type("Rabbit", 20, 500, 20, 10, 0, 0)
        def __init__(self, id, name, lvl, hp, xp, arm, atk, mp, marm, agi, spells, abilities, r_spell):
            self.id = id
            self.name = name
            self.job = name
            self.lvl = lvl
            self.hp = hp
            self.xp = xp
            self.arm = arm
            self.atk = atk
            self.mp = mp
            self.marm = marm
            self.agi = agi
            self.spells = spells
            self.abilities = abilities
            self.maxhp = hp
            self.maxmp = mp
            self.defhp = hp
            self.defmp = mp
            self.defatk = atk
            self.defmarm = marm
            self.defagi = agi
            self.dead = False
            self.turn = 0
            self.items = {}
            self.xptn = random.randrange(40,60,1)
            self.origtn = self.xptn
            self.maxlvl = 60
            self.r_spells = {'fire' : r_spell[0], 'water' : r_spell[1], 'ice' : r_spell[2], 'thunder' : r_spell[3], 'arcane' : r_spell[4]}
            #self.kwargs = [kwargs]
            #for n,v in kwargs.items():
            #   setattr(self, n, v)
            self.poisondmg = 0
            self.status = []
            #print self.name
            
        def __repr__(self):
            return self.name    
        
        def get_status(self):
            spell_names = ""
            ability_names = ""
            status_names = ""
            if self.spells:
                spell_names = ', '.join([spell_id[x].name for x in self.spells])
            if self.abilities:
                ability_names = ', '.join([ability_id[x].name for x in self.abilities])
            if self.status:
                status_names = ', '.join([status_id[x].name for x in self.status])
            print "Name: "+self.name, "("+self.job+")\n", "Level:", self.lvl, "\nHP:", self.hp, "/", self.maxhp, "\nMP:", self.mp, "/", self.maxmp,\
                "\nXP:", self.xp, "/", self.xptn,\
                "\nArmor:", self.arm, "\nAttack Power:", self.atk, "\nAgility:", self.agi,\
                "\nBase Magic Armor:", self.marm,\
                "\nSpell Resistances:", " Fire:", self.r_spells['fire'], " Water:", self.r_spells['water'], " Ice:", self.r_spells['ice'], " Thunder:", self.r_spells['thunder'], " Arcane:", self.r_spells['arcane'],\
                "\nSpells:", spell_names, "\nAbilities:", ability_names,\
                "\nStatus Effects:", status_names
        
        def get_hp(self):
            return self.hp
        
        def set_hp(self, hp):
            self.hp = hp
            
        def get_mp(self):
            return self.mp
        
        def set_mp(self, mp):
            self.mp = mp

        def level_up(self):
            if self.lvl < self.maxlvl:
                orighp = self.maxhp
                origmp = self.maxmp
                self.lvl += 1
                if self.lvl < 15:
                    self.xptn = math.trunc(round((self.origtn * 1.3) * self.lvl))
                elif self.lvl >= 15 and self.lvl < 30:
                    self.xptn = math.trunc(round((self.origtn * 1.1) * self.lvl))
                elif self.lvl >= 30 and self.lvl < 50:
                    self.xptn = math.trunc(round((self.origtn * 1.05) * self.lvl))
                elif self.lvl >= 50 and self.lvl <= 60:
                    self.xptn = math.trunc(round((self.origtn * 1.025) * self.lvl))
                self.xptn = math.trunc(round(self.xptn))
                self.maxhp += math.trunc(round(self.lvl * random.choice([3.0, 3.5, 4.0])))
                self.maxmp += math.trunc(round(self.lvl * random.choice([3.0, 3.5, 4.0])))
                self.atk += random.choice([1.2, 1.4, 1.6])
                self.agi += random.choice([1.2, 1.4, 1.6])
                self.xp = 0
                self.marm += 1
                self.hp = self.maxhp
                self.mp = self.maxmp
                print "%s has levelled up to Level %d!" % (self.name, self.lvl)
                print "%s has gained %d health points and %d mana points!" % (self.name, (self.hp - orighp), (self.mp - origmp))  
            else:
                print "%s is already max level!" % (self.name)
                

#
#   Magic Class
#

class Magic:
        #Define spells by: class Spell(Magic)  ..  spell_1 = Spell("Fire Blast", 20, 10)
        def __init__(self, id, name, mpcost, mindmg, maxdmg, type, s_flag, s_action):
            self.id = id
            self.name = name
            self.mpcost = mpcost
            self.mindmg = mindmg
            self.maxdmg = maxdmg
            self.type = type
            self.s_flag = s_flag
            self.s_action = s_action
        
        def __repr__(self):
            return self.name

#
#   Physical Ability Class
#

class Physical:
        #Define abilities by: class Ability(Physical)  ..  ability_1 = Ability("Rake", 10)
        def __init__(self, id, name, mindmg, maxdmg, s_flag, s_action):
            self.id = id
            self.name = name
            self.mindmg = mindmg
            self.maxdmg = maxdmg
            self.s_flag = s_flag
            self.s_action = s_action
            
        def __repr__(self):
            return self.name


#
#   Item/Consumable Class
#

class Consumable:
        def __init__(self, id, name, amount, type):
            self.id = id
            self.name = name
            self.amount = amount
            self.type = type
            return name
            
        def use(self, target):
            if self.type in "heal_hp":
                target.hp =+ self.amount
                if target.hp > target.maxhp:
                    target.hp = target.maxhp
                party.items[str(self)] -= 1
                if party.items[str(self)] <= 0:
                    del party.items[str(self)]
                print "%s was healed for %d and is now at %d HP!" % (target.name, self.amount, target.hp)
                return

        def __repr__(self):
            return self.name


#
#   Party Class
#

class Party:
        #Define Party: var = Party(size, members)
        def __init__(self, maxsize, membercopy):
            self.maxsize = maxsize
            self.members = []
            self.items = {}
            self.gold = 0
            
            while len(self.members) < maxsize:
                self.members += membercopy

            self.partyhp = self.get_hp()
            
        def get_hp(self):
            total = 0
            for x in self.members:
                total += x.hp
            return total
            
        def set_xp(self, xp):
            for x in self.members:
                if x.hp > 0:
                    x.xp += xp
                else:
                    return
        
        def avg(self):
            return sum([x.lvl for x in self.members]) / len(self.members)
            
        def __repr__(self):
            return ', '.join([x.name for x in self.members])


#
#   Begin Class Derivations
#

class Mob(Entity):
    def __init__(self, id, name, lvl, hp, xp, arm, atk, mp, marm, agi, spells, abilities, r_spell, gold, items, info):
        Entity.__init__(self, id, name, lvl, hp, xp, arm, atk, mp, marm, agi, spells, abilities, r_spell)
        self.info = info
        self.gold = gold
        self.items = items
        mob_id[self.id] = self
        
    def get_status(self):
        spell_names = ""
        ability_names = ""
        status_names = ""
        if self.spells:
            for x in self.spells:
                spell_names += spell_id[x].name
                spell_names += ", "
            if spell_names.endswith(' '):
                spell_names = spell_names[:-2]
        if self.abilities:
            for x in self.abilities:
                ability_names += ability_id[x].name
                ability_names += ", "
            if ability_names.endswith(' '):
                ability_names = ability_names[:-2]
        if self.status:
            for x in self.status:
                status_names += status_id[x].name
                status_names += ", "
            if status_names.endswith(' '):
                status_names = status_names[:-2]
        print "Name: "+self.name, "\nLevel:", self.lvl, "\nHP:", self.hp, "\nMP:", self.mp,\
            "\nXP:", self.xp,\
            "\nArmor:", self.arm, "\nAttack Power:", self.atk, "\nAgility:", self.agi,\
            "\nBase Magic Armor:", self.marm,\
            "\nSpell Resistances:", " Fire:", self.r_spells['fire'], " Water:", self.r_spells['water'], " Ice:", self.r_spells['ice'], " Thunder:", self.r_spells['thunder'], " Arcane:", self.r_spells['arcane'],\
            "\nSpells:", spell_names, "\nAbilities:", ability_names,\
            "\nInfo:", self.info

class Human(Entity):
    def __init__(self, id, name, lvl, hp, xp, arm, atk, mp, marm, agi, spells, abilities, r_spell):
        Entity.__init__(self, id, name, lvl, hp, xp, arm, atk, mp, marm, agi, spells, abilities, r_spell)
        human_id[self.id] = self
        
class Summon(Entity):
    def __init__(self, id, name, lvl, hp, xp, arm, atk, mp, marm, agi, spells, abilities, r_spell):
        Entity.__init__(self, id, name, lvl, hp, xp, arm, atk, mp, marm, agi, spells, abilities, r_spell)
        summon_id[self.id] = self
  
class Spell(Magic):
    def __init__(self, id, name, mpcost, mindmg, maxdmg, type, s_flag, s_action):
        Magic.__init__(self, id, name, mpcost, mindmg, maxdmg, type, s_flag, s_action)
        spell_id[self.id] = self
        
class Ability(Physical):
    def __init__(self, id, name, mindmg, maxdmg, s_flag, s_action):
        Physical.__init__(self, id, name, mindmg, maxdmg, s_flag, s_action)
        ability_id[self.id] = self

class Item(Consumable):
    def __init__(self, id, name, amount, type):
        Consumable.__init__(self, id, name, amount, type)
        item_id[self.id] = self

#
#   End Class Derivations
#


#
#   Begin Mob/Human/Item/Summon/Spell/Ability Definitions
#

#  - Spider, Goblin, Zombie, (Fire/Ice Wraith), Cobra, Bat, Toad, Bomb, Snake, Black Mamba, Moth, Imp, Slime, Bandit, Bandit Leader,
#    Box.
#           ID  NAME                LVL      HP     XP     ARM     ATK     MP      MARM      AGI     SPELLS         ABILITIES   Resistances [Fire, Water, Ice, Thunder, Arcane]     Gold        Items       Info
mob_1 = Mob(1,  "Rabbit",           1,       10,    6,     0,      2,      0,      0,        10,         [],            [1,2],              [5,    0,     5,   0,       0],         5,          [1],            "A small brown hare.")
mob_2 = Mob(2,  "Wolf",             2,       20,    10,    2,      5,      10,     0,        15,         [],            [2],                [0,    0,     0,   0,       0],         5,          [1],            "A battle-worn grey wolf.")
mob_3 = Mob(3,  "Spider",           1,       15,    10,    0,      4,      10,     0,        12,         [],            [2],                [0,    0,     0,   0,       0],         5,          [1],            "A dog-sized poisonous spider.")
mob_4 = Mob(4,  "Cobra",            2,       30,    15,    5,      6,      10,     0,        10,         [],            [2, 6],             [0,    0,     0,   0,       0],         5,          [1],            "La paura del Cobra.")
mob_5 = Mob(5,  "Moth",             3,       40,    20,    3,      5,      10,     5,        13,         [],            [6],                [0,    0,     0,   0,       0],         5,          [1],            "A very hungry moth, aching of starvation for your robes.")
mob_6 = Mob(6,  "Imp",              3,       45,    25,    2,      3,      30,     5,        10,         [1, 2],        [2],                [0,    0,     0,   0,       0],         5,          [1],            "Can't we all justI get along?")
mob_7 = Mob(7,  "Toad",             3,       50,    30,    0,      2,      10,     0,        15,         [],            [7],                [0,    0,     0,   0,       0],         5,          [1],            "Ribbit.")
mob_8 = Mob(8,  "Ogre",             10,      200,   200,   10,     10,     10,     0,        5,          [],            [3, 4, 5],          [0,    0,     0,   0,       0],         5,          [1],            "Ogre, SMASH!")
mob_9 = Mob(9,  "Black Mamba",      33,      200,   1124,  24,     30,     0,      0,        50,         [],            [8],                [0,    0,     0,   0,       0],         5,          [1],            "Kobe!")

#               ID  NAME            LVL     HP       XP     ARM      ATK     MP      MARM    AGI    SPELLS      ABILITIES     Resistances [Fire, Water, Ice, Thunder, Arcane]
fighter = Job('Fighter', attr_ranges={'strength': (5,7,0,3), 'acc': (10,14,0,3)})
human_2 = Human(2,  "Thief",        1,      20,      0,     4,       2,      10,     0,      15,        [],     [4, 5],                   [0,    0,     0,   0,       0])
human_3 = Human(3,  "Mage",         1,      20,      0,     0,       0,      30,     0,      10,        [1, 2], [],                       [0,    0,     0,   0,       0])
#                 ID    NAME            LVL     HP       XP     ARM      ATK     MP      MARM    AGI    SPELLS      ABILITIES     Resistances [Fire, Water, Ice, Thunder, Arcane]
summon_1 = Summon(1,    "Ifrit",        10,     250,     0,     5,       15,     300,    0,      20,    [1, 2],     [],                       [0,    0,     0,   0,       0])
#               ID  NAME                    MP          MINDMG          MAXDMG      Type        Special Flag            Special Action
spell_1 = Spell(1,  "Fire Blast",           6,          6,              10,         "fire",     False,                  0)
spell_2 = Spell(2,  "Ice Bolt",             4,          4,              8,          "ice",      False,                  0)
spell_3 = Spell(3,  "Meteor",               25,         35,             50,         "fire",     False,                  0)
#             ID    NAME        Amount      Type
item_1 = Item(1,    "Potion",   20,         "heal_hp")
#                   ID    NAME                          MINDMG          MAXDMG      Special Flag            Special Action
ability_1 = Ability(1,    "Rake",                       3,              5,          False,                  0)
ability_2 = Ability(2,    "Bite",                       5,              7,          False,                  0)
ability_3 = Ability(3,    "Crush",                      20,             25,         False,                  0)
ability_4 = Ability(4,    "Kick",                       6,              9,          False,                  0)
ability_5 = Ability(5,    "Punch",                      5,              7,          False,                  0)
ability_6 = Ability(6,    "Poison Fang",                8,              10,         False,                  0)
ability_7 = Ability(7,    "Croak",                      0,              0,          True,                   "print \"Toad croaks.\"")
ability_8 = Ability(8,    "Fang Dunk",                  25,             50,         False,                  0)
