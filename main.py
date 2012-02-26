#!/usr/bin/env python

#TO-DO:
# Framework = DONE - Add Inventory/Items/Equipment
# Framework = DONE - Multi-level spells (Powering up to cast)
#  LATER - Add weight to attacks/spells (Heal based on other party member's HP percentage, Status attacks, probability for using certain atks)
# Mobs/Humans
# HALF DONE - Add moooore mobs.
#  - Spider, Goblin, Zombie, (Fire/Ice Wraith), Cobra, Bat, Toad, Bomb, Snake, Black Mamba, Moth, Imp, Slime, Bandit, Bandit Leader,
#    Box.


#URGENT TO-DO
#[DONE] 1. Add case-insensitivity (Undercase all comparisons?)
#[DONE] 2. Stack items in inventory (Use dictionary with Names as IDs and values as quantity?)
# 3. Do user-interactive battle system
#
#    Notes: Test using a different cmd.loop for battles, rename the "main" loop to menu/title screen.
#           Possibly giving a new game/load/options selection (Maybe wait till pygmy is integrated)
#           How should I do turns? Variable, do the whole based on agi turn based system?
#           Or keep it as I have it by grouping all together and random.choice/popping?
#           Write new function with different situations to test alternatives?
#           
#           Add those new mobs, still gotta tweak with specific stats to make it more balanced.
#           [Done!/?] [Also, rewrite battles for generating the mob party to be within the average level of human
#           party within 2 or so levels.]
#
#           Also, add checks to see if mob has a healing spell, if so, cast whenever possible on
#           injured allies. Same with beneficial buffs such as haste and slow on enemies.
#
#           Add the aforementioned beneficial buffs!
#
#           Should I slim down the attack function and remove mob/human flags and do all the decision
#           making outside of the function (def think() for situations in entity class?)
#
#           Get those darned summons to work, was able to get the party to be replaced by Summoned
#           creature but, unable to replace party back into play.
#
#           Also try charging up/multi-phase spells such as Bomb's charge up and explode which
#           will kill a random party member, and setting up events defined in mobs initializations
#           using the s_flag/s_action parameters. (Check for better solution/Pre-Defined event
#           parties?)
#
#           Get equipment working, try only increasing one stat at first, maybe upping critical chance
#           by 2% while wearing, add check for attacker/defender's equipment enchantments
#
#           When tablet-get, draw some concept art for base human entities, thinking of doing a style
#           such as sorta cartoony mini-people, but with no mouths. Also, gotta do hats, bitches love hats.
#
#           Maybe also scarves, they get ladies too. Ascots!
#
#           Getting ahead of myself, though.
#
#           Worry about later: Story, Sounds, Final Art Style

import random, math, copy, time, cmd, pickle, os, re

from pprint import pprint
from entity import *
from spell import *

def quit():
    return

debug = 1
clr = '\x1b[1;1H\x1b[J'
summon = False
mob_id = {}
human_id = {}
summon_id = {}
spell_id = {}
ability_id = {}
status_id = {}
item_id = {}
party = []
m_party = []
group = []

if not os.path.exists('./save/'):
    os.mkdir('./save/')
                            
def attack(h_flag, attacker, defender, spell, ability):
        choices = []
        if len(attacker.spells):
            spell = spell_id[random.choice(attacker.spells)]
            if spell.s_flag:
                exec(spell.s_action)
                return
            else:
                s_resist = defender.marm
                if defender.r_spells[spell.type]:
                    s_resist =+ math.trunc(round(defender.r_spells[spell.type]))
                s_dmg = random.randrange(spell_id[spell.id].mindmg, spell_id[spell.id].maxdmg, 1)
                s_crittotal = math.trunc(round(s_dmg * random.uniform(2,3)))
                s_crittotal_orig = s_crittotal
                if s_crittotal <= 0:
                    s_crittotal = spell_id[spell.id].mindmg + spell_id[spell.id].maxdmg / 2
                choices += [spell]
        elif not attacker.spells:
            spell = 0
        if len(attacker.abilities):
            ability = ability_id[random.choice(attacker.abilities)]
            if ability.s_flag:
                exec(ability.s_action)
                return
            else:   
                a_dmg = random.randrange(ability_id[ability.id].mindmg, ability_id[ability.id].maxdmg, 1)
                a_crittotal = round((a_dmg * random.randint(2,3))) + attacker.atk
                a_crittotal_orig = a_crittotal
                a_crittotal = round(a_crittotal_orig - defender.arm)
                a_crittotal_orig -= a_crittotal
                if a_crittotal <= 0:
                    a_crittotal = ability_id[ability.id].mindmg + ability_id[ability.id].maxdmg / 2
                choices += [ability]
        elif not attacker.abilities:
            ability = 0
        critcheck = random.randint(1,10)
        choice = random.choice(choices)
        dodgecheck = (random.randint(1,100) + defender.agi - attacker.agi)
        orighp = defender.get_hp()
        if choice is spell and attacker.mp < choice.mpcost:
            print "%s tried casting %s but it fizzled!" % (attacker.name, choice.name)
        elif choice is spell and critcheck >= 8:
            if dodgecheck < 90:
                if math.trunc(round(s_crittotal - s_resist)) < 0:
                    healed = math.trunc(round(math.fabs(s_crittotal - s_resist)))
                    defender.set_hp(math.trunc(round(defender.get_hp() - round(s_crittotal - s_resist))))
                    print "%s (%d) was healed by %s for %d with %s! %s is now at %d health!" % (defender.name, orighp, attacker.name, healed, spell_id[choice.id].name, defender.name, defender.get_hp())
                elif math.trunc(round(defender.get_hp() - round(s_crittotal - s_resist))) >= 0:
                    defender.set_hp(math.trunc(round(defender.get_hp() - round(s_crittotal - s_resist))))
                    if defender.get_hp() <= 0:
                        print "%s (%d) was crit by %s for %d (%d resisted) with %s! %s is now dead!" % (defender.name, orighp, attacker.name, (s_crittotal - s_resist), s_resist, spell_id[choice.id].name, defender.name)
                        defender.set_hp(0)
                        attacker.mp -= choice.mpcost
                        if attacker.mp < 0:
                            attacker.mp = 0
                    elif defender.get_hp() > 0:
                        print "%s (%d) was crit by %s for %d (%d resisted) with %s! %s is now at %d health!" % (defender.name, orighp, attacker.name, (s_crittotal - s_resist), s_resist, spell_id[choice.id].name, defender.name, defender.get_hp())
                        attacker.mp -= choice.mpcost
                        if attacker.mp < 0:
                            attacker.mp = 0
                    return
                elif dodgecheck >= 90:
                    print "%s casts %s... but %s dodged!" % (attacker.name, choice.name, defender.name)
        elif choice is spell and critcheck < 8:
            if dodgecheck < 90:
                if math.trunc(round(s_dmg - s_resist)) < 0:
                    healed = math.trunc(round(math.fabs(s_dmg - s_resist)))
                    defender.set_hp(math.trunc(math.fabs(round(defender.get_hp() - (s_dmg - s_resist)))))
                    print "%s (%d) was healed by %s for %d with %s! %s is now at %d health!" % (defender.name, orighp, attacker.name, healed, spell_id[choice.id].name, defender.name, defender.get_hp())
                elif math.trunc(round(s_dmg - s_resist)) >= 0:
                    defender.set_hp(math.trunc(round(defender.get_hp() - (s_dmg - s_resist))))
                    if defender.get_hp() <= 0:
                        print "%s (%d) was hit by %s for %d (%d resisted) with %s! %s is now dead!" % (defender.name, orighp, attacker.name, (s_dmg - s_resist), s_resist, spell_id[choice.id].name, defender.name)
                        defender.set_hp(0)
                        attacker.mp -= choice.mpcost
                        if attacker.mp < 0:
                            attacker.mp = 0
                    elif defender.get_hp() > 0:
                        print "%s (%d) was hit by %s for %d (%d resisted) with %s! %s is now at %d health!" % (defender.name, orighp, attacker.name, (s_dmg - s_resist), s_resist, spell_id[choice.id].name, defender.name, defender.get_hp())
                        attacker.mp -= choice.mpcost
                        if attacker.mp < 0:
                            attacker.mp = 0
                elif dodgecheck >= 90:
                    print "%s attacks with %s... but %s dodged!" % (attacker.name, choice.name, defender.name) 
                return
        elif choice is ability and critcheck >=8:
            if dodgecheck < 90:
                if a_crittotal < defender.arm:
                    print "%s tried attacking %s with %s... but it had no effect!" % (attacker.name, defender.name, ability_id[choice.id].name)
                    return
                defender.set_hp(math.trunc(round(defender.get_hp() - a_crittotal)))
                if defender.get_hp() <= 0:
                    print "%s (%d) was crit by %s for %d (%d resisted) with %s! %s is now dead!" % (defender.name, orighp, attacker.name, a_crittotal, a_crittotal_orig, ability_id[choice.id].name, defender.name)
                    defender.set_hp(0)
                elif defender.get_hp() > 0:
                    print "%s (%d) was crit by %s for %d (%d resisted) with %s! %s is now at %d health!" % (defender.name, orighp, attacker.name, a_crittotal, a_crittotal_orig, ability_id[choice.id].name, defender.name, defender.get_hp())
                return
            elif dodgecheck >= 90:
                print "%s attacks with %s... but %s dodged!" % (attacker.name, choice.name, defender.name)
        elif choice is ability and critcheck < 8:
            if dodgecheck < 90:
                if (a_dmg + attacker.atk) < defender.arm:
                    print "%s tried attacking %s with %s... but it had no effect!" % (attacker.name, defender.name, ability_id[choice.id].name)
                    return
                defender.set_hp(math.trunc(round(defender.get_hp() - ((a_dmg + attacker.atk) - defender.arm))))
                if defender.get_hp() <= 0:
                    print "%s (%d) was hit by %s for %d (%d resisted) with %s! %s is now dead!" % (defender.name, orighp, attacker.name,  (a_dmg + attacker.atk) - defender.arm, defender.arm, ability_id[choice.id].name, defender.name)
                    defender.set_hp(0)
                elif defender.get_hp() > 0:
                    print "%s (%d) was hit by %s for %d (%d resisted) with %s! %s is now at %d health!" % (defender.name, orighp, attacker.name, (a_dmg + attacker.atk) - defender.arm, defender.arm, ability_id[choice.id].name, defender.name, defender.get_hp())
            elif dodgecheck >= 90:
                print "%s attacks with %s... but %s dodged!" % (attacker.name, choice.name, defender.name) 
            return
        return
            
def target(target):
    if target is "mobs" and [x for x in m_party.members if x.hp <= 0]:
        return 0
    if target is "mobs":
        targ = [x for x in m_party.members if x.hp > 0]
        return random.choice(targ)
    elif target is "human":
        targ = [x for x in party.members if x.hp > 0]
        return random.choice(targ)
    else:
        return

def m_party_gen():
    global party    
    global m_party
    p_avg = 0
    m_party_gen.m_avg = 0
    m_lvls = [x.lvl for x in mob_id.values()]
    for x in party.members:
        p_avg += x.lvl
    p_avg = p_avg / len(party.members)
    m_party_gen.tempparty = []
    #while m_avg < range(p_avg-2, p_avg+3):
    def m_populate():
        m_party_gen.maxsize = random.randrange(1,3,1)
        del m_party_gen.tempparty[:]
        m_party_gen.m_avg = 0
        while len(m_party_gen.tempparty) < m_party_gen.maxsize:
            ra_choice = random.choice(mob_id.values())
            m_party_gen.tempparty += copy.deepcopy([ra_choice])
        for x in m_party_gen.tempparty:
            m_party_gen.m_avg += x.lvl
        m_party_gen.m_avg = m_party_gen.m_avg / len(m_party_gen.tempparty)
    
    m_party_gen.flag = False
    while m_party_gen.flag is False:
        m_populate()
        if str(m_party_gen.m_avg) in str(range(p_avg-2, p_avg+3)):
            m_party = Party(m_party_gen.maxsize, m_party_gen.tempparty)
            m_party_gen.flag = True

        elif str(m_party_gen.m_avg) < str(p_avg-6):
            m_populate()
    
        elif str(m_party_gen.m_avg) > str(range(p_avg-2, p_avg+3)):
            m_populate()
        
        else:
            m_populate()

def party_gen():
    global party
    tempparty = []
    maxsize = random.randint(1,3)
    while len(tempparty) < maxsize: 
        tempparty += copy.deepcopy([random.choice(human_id.values())])
    party = Party(maxsize, tempparty)

# Default attribute ranges (min_base, max_base, min_per_level, max_per_level)
#   Max HP    (maxhp):     17, 23, 1, 3
#   Max MP    (maxmp):     17, 23, 1, 3
#   Attack    (atk):       8,  12, 0, 2
#   Defense   (def):       8,  12, 0, 2
#   Accuracy  (acc):       8,  12, 0, 2
#   Evasion   (eva):       8,  12, 0, 2
#   Magic Atk (matk):      8,  12, 0, 2
#   Magic Def (mdef):      8,  12, 0, 2
#   Magic Acc (macc):      8,  12, 0, 2
#   Magic Eva (meva):      8,  12, 0, 2
#   Goblin, Zombie, (Fire/Ice Wraith), Bat, Bomb, Slime, Box

job_Rabbit = Job('Rabbit', attr_ranges={'atk': (6,10,0,2), 'def': (6,10,0,2), 'eva': (10,14,0,4)})
job_Wolf   = Job('Wolf',   attr_ranges={'eva': (11,15,0,3)})
job_Spider = Job('Spider', attr_ranges={'def': (6,10,0,2), 'eva': (9,13,0,3)})
job_Serpent = Job('Serpent',  attr_ranges={'atk': (7,11,0,3), 'acc': (10,14,0,3), 'eva': (10,14,0,3)})
job_Moth    = Job('Moth',   attr_ranges={'eva': (12,16,0,2), 'mdef': (10,14,0,2), 'meva': (10,14,0,2)})
job_Demon   = Job('Demon',  attr_ranges={'maxhp': (20,26,1,3), 'maxmp': (19,25,1,3), 'matk': (10,14,0,2), 'mdef': (10,14,0,2), 'macc': (9,11,0,2)})
job_Frog    = Job('Frog', attr_ranges={'def': (6,10,0,2)})
job_Humanoid = Job('Humanoid')
job_magical_Summon = Job('Guardian', attr_ranges={'maxhp': (22,28,2,6), 'maxmp': (22,26,2,6), 'atk': (10,14,0,2), 'def': (12,16,1,3), 'acc': (16,20,1,3), 'eva': (16,20,1,3), 'matk': (16,20,1,2), 'mdef': (16,20,2,6)})
job_physical_Summon = Job('Guardian', attr_ranges={'maxhp': (22,28,3,8), 'maxmp': (22,26,2,6), 'atk': (10,14,2,6), 'def': (12,16,2,6), 'acc': (16,20,2,6), 'eva': (16,20,2,6), 'matk': (16,20,2,4), 'mdef': (16,20,1,3)})
job_Fighter = Job('Fighter', attr_ranges={'atk': (10,12,0,3), 'def': (10,12,0,3)})
job_Thief = Job('Thief', attr_ranges={'atk': (9,11,0,2), 'acc': (10,14,0,3), 'eva': (10,14,0,3)})
job_Mage = Job('Mage', attr_ranges={'atk': (4,8,0,1), 'def': (4,8,0,2), 'matk': (10,14,0,3), 'mdef': (10,14,0,3), 'macc': (10,14,0,3), 'meva': (10,14,0,3)})

#
#   Begin Specific Entities
#

ent_blackmamba = Entity(job_Serpent, "Black Mamba")
ent_cobra = Entity(job_Serpent, "Paura")
ent_ogre = Entity(job_Humanoid, "Ogre")
ent_ifrit = Entity(job_magical_Summon, "Ifrit")
ent_jackie = Entity(job_Fighter, "Jackie Chan")
ent_shad = Entity(job_Thief, "Shad Gaspard")
ent_gandalf = Entity(job_Mage, "Gandalf the Grey")

#   Test Party
party = Party((ent_jackie, ent_shad, ent_gandalf))

#
#   Begin Spell Declarations
#

spell_fireball = Spell("Fire Ball", 4, "damage health")
spell_icebolt = Spell("Ice Bolt", 2, ("damage health", "status slow"))
spell_meteor = Spell("Meteor", 4, "damage health")

#
#   Begin Item Declarations
#

#item_potion = Item("Potion", 20, "heal hp")


#
#   Begin Ability Declarations
#

ability_bite = Spell("Bite", 0, "damage health")
ability_rake = Spell("Rake", 0, "damage health")
ability_crush = Spell("Crush", 0, "damage health")
ability_kick = Spell("Kick", 0, ("damage health", "status confuse"))
ability_punch = Spell("Punch", 0, "damage health")
ability_poisonfang = Spell("Poison Fang", 0, ("damage health", "status poison"))
ability_croak = Spell("Croak", 0, "do croak")
ability_fangdunk = Spell("Fang Dunk", 0, "twotoothed jam")

#Define Predetermined Mob Parties
#mob_p1 = [copy.deepcopy(mob_id[1])] 
#mob_p2 = [copy.deepcopy(mob_id[1]), copy.deepcopy(mob_id[1])]
#mob_p3 = [copy.deepcopy(mob_id[1]), copy.deepcopy(mob_id[1]), copy.deepcopy(mob_id[1])]

class b_con(cmd.Cmd):
    
    def __init__(self):
        self.completekey = None
        self.prompt = "=>> "

    def do_exit(self, args):
        print "blargh"
        return -1

    def do_quit(self, args):
        return -1
        
    def do_EOF(self, args):
        return self.do_exit(args)

    def postloop(self):
        print "postloop()"

class Battle(b_con):
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.completekey = None
        self.prompt = "==>> "
        print '\x1b[1;1H\x1b[J'
        m_party_gen()
        global group 
        group = party.members + m_party.members
        print "A group consisting of %s appears!" % (m_party)
        self.do_fight()
        
    def do_fight(self):
        global group    
        while (party.get_hp() > 0) and (m_party.get_hp() > 0):
            c = random.choice(group)
            if c.__class__.__name__ is "Mob":
            #0 = MOB ATTACKING/1 = HUMAN ATTACKING, ATTACKER, DEFENDER
                attack(0, c, random.choice(party.members), 0, 0)
                c.turn =+ 1
                group.remove(c)
                if not group:
                    group = party.members + m_party.members
                    random.shuffle(group)
            elif c.__class__.__name__ is "Human":
                print "It is %s's turn!" % (c)
                turn_complete = False
                while turn_complete is False:
                    if c.abilities:
                        for x in c.abilities:
                            print ability_id[x]
                    if c.spells:
                        for x in c.spells:
                            print spell_id[x]
                    turn_complete = True
                c.turn =+ 1
                group.remove(c)
                if not group:
                    group = party.members + m_party.members
                    random.shuffle(group)
        if (party.get_hp() <= 0):
            print "Party\'s Over!ddd"
            time.sleep(2)
            console = P_menu()
            console.cmdloop()
        elif (m_party.get_hp() <= 0):
            totalxp = math.trunc(round(math.fsum([x.xp for x in m_party.members])))
            splitxp = math.trunc(round(totalxp / len(party.members)))
            party.set_xp(splitxp)
            print "Monster Party\'s Over!"
            lootbuffer = {}
            goldbuffer = 0
            for x in party.members:
                if x.xp >= x.xptn:
                    x.level_up()
            for x in m_party.members:
                lootchance = random.randrange(1,100,1)
                goldbuffer += x.gold
                if lootchance >= 50:
                    i_ran = item_id[random.choice(x.items)]
                    if not lootbuffer:
                        lootbuffer[str(i_ran)] = 1
                    else:
                        lootbuffer[str(i_ran)] += 1
            if lootbuffer:
                for each in lootbuffer:
                    if not party.items:
                        party.items[str(each)] = lootbuffer[each] 
                    else:
                        party.items[str(each)] += lootbuffer[each]
                party.gold += goldbuffer
                i_buf = ""
                for x in party.items:
                    i_buf += "%s x%d" % (x, lootbuffer[x])
                print "Party receives: %s and %d gold!" % ( i_buf, goldbuffer )
                time.sleep(2)
                console = P_menu()
                console.cmdloop()
            if goldbuffer and not lootbuffer:
                party.gold += goldbuffer
                print "Party receives: %d gold!" % (goldbuffer)
                time.sleep(2)
                console = P_menu()
                console.cmdloop()
        print "\n"

    def do_status(self, args=''):
        print '\x1b[1;1H\x1b[J'
        if len(args) > 0:
            args = args.lower()
            ents_by_name = {mob.name.lower(): mob for mob in mob_id.values()}
            ents_by_name.update({member.name.lower(): member for member in party.members})
            pprint(ents_by_name)
            if args in ents_by_name:
                print "============"
                ents_by_name[args].get_status()
                print "============\n"
            else:
                print "============"
                print "Not Found :("
                print "============\n"
        else:
            print "============"
            for x in party.members:
                status_buf = ""
                if x.status:
                    for x in x.status:
                        status_buf = ', '.join(x.status)
                if not x.status:
                    status_buf = "None"
                print x.name+" ("+x.job+")\n"+" | Level:", x.lvl, "| HP:", x.hp, "| MP:", x.mp, "| Xp:", x.xp, "| Xp till Level:", x.xptn - x.xp, "| Status:", status_buf
            i_buf = ""
            for x in party.items:
                i_buf += "%s x%d" % (x, party.items[x])
            print "Items: %s" % (i_buf)
            print "============\n"      
            print "============"
            for x in m_party.members:
                status_buf = ""
                if x.status:
                    for x in x.status:
                        status_buf = ', '.join(x.status)
                if not x.status:
                    status_buf = "None"
                print x.name+"\n"+" | Level:", x.lvl, "| HP:", x.hp, "| MP:", x.mp, "| Status:", status_buf
            print "============\n"

class Menu(b_con):
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.completekey = None
        self.prompt = "=>> "
        self.intro = self.do_start(self)
        
    def do_start(self, args):
        print '\x1b[1;1H\x1b[J'
        print "1. New Game", "\n2. Load Game", "\n3. Exit"
    
    def default(self, args):
        if args is "1":
            if os.path.isfile("./save/party_members.dat"):
                print "Save files exist! Are you sure? (y/n)"
                x = raw_input()
                if x is "y":
                    os.remove('./save/party_members.dat')
                    os.remove('./save/party_gold.dat')
                    os.remove('./save/party_items.dat')
                    print '\x1b[1;1H\x1b[J'
                    console = P_menu()
                    console.cmdloop()
                else:
                    self.do_start(self)
            else:
                print '\x1b[1;1H\x1b[J'
                console = P_menu()
                console.cmdloop()
        elif args is "2":
            if os.path.isfile("./save/party_members.dat"):
                console = P_menu()
                console.cmdloop()
            else:
                print "Save files do not exist! Please start a new game."
                time.sleep(2)
                self.do_start(self)
        elif args is "3":
            return -1
        else:
            print "Invalid option! Please enter 1, 2 or 3."

class P_menu(b_con):
    global party
    global m_party
    global debug
    debug = 0
    tempparty = []
    #tempparty += copy.deepcopy([human_id[1]])
    #tempparty += copy.deepcopy([human_id[2]])
    #tempparty += copy.deepcopy([human_id[3]])
    #party = Party(3, tempparty)
    tempparty = []
    
    def __init__(self):
        cmd.Cmd.__init__(self)
        self.completekey = None
        self.prompt = "=>> "
        self.intro = self.do_start(self)

    def do_start(self, args):
        print '\x1b[1;1H\x1b[J'
        if os.path.isfile("./save/party_members.dat"):
            party.members = pickle.load(open('./save/party_members.dat', 'r+'))
            party.items = pickle.load(open('./save/party_items.dat', 'r+'))
            party.gold = pickle.load(open('./save/party_gold.dat', 'r+'))
            self.do_status()
            return
        for x in party.members:
            print "Name your", x.job+": "
            x.name = raw_input()
        print "\n============"
        for x in party.members:
            print x.name+" ("+x.job+")"+"   | Level:", x.lvl, "| HP:", x.hp, "| MP:", x.mp
        print "============\n"
        self.do_save(self)
            
    def do_rename(self, args):
        print '\x1b[1;1H\x1b[J'
        for x in party.members:
            print "Name your", x.job+": "
            x.name = raw_input()
        print "\n"
        for x in party.members:
            print x.name+" ("+x.job+")"+"   | Level:", x.lvl, "| HP:", x.hp, "| MP:", x.mp

#   def do_status(self, args):
#       print '\x1b[1;1H\x1b[J'
#       if re.match("^[A-Za-z0-9]", str(args)):
#           for x in party.members:
#               if str.lower(x.name) in str.lower(str(args)):
#                   print "============"
#                   x.get_status()
#                   print "============\n"
#                   return
#           for x in mob_id:
#               if str.lower(mob_id[x].name) in str.lower(str(args)):
#                   print "============"
#                   mob_id[x].get_status()
#                   print "============\n"
#                   return

    def do_status(self, args=''):
        print '\x1b[1;1H\x1b[J'
        if len(args) > 0:
            args = args.lower()
            ents_by_name = {mob.name.lower(): mob for mob in mob_id.values()}
            ents_by_name.update({member.name.lower(): member for member in party.members})
            pprint(ents_by_name)
            if args in ents_by_name:
                print "============"
                ents_by_name[args].get_status()
                print "============\n"
            else:
                print "============"
                print "Not Found :("
                print "============\n"
        else:
            print "============"
            for x in party.members:
                print x.name+" ("+x.job+")\n"+" | Level:", x.lvl, "| HP:", x.hp, "| MP:", x.mp, "| Xp:", x.xp, "| Xp till Level:", x.xptn - x.xp
            print "Gold: %d" % (party.gold)
            i_buf = ""
            for x in party.items:
                i_buf += "%s x%d" % (x, party.items[x])
            print "Items: %s" % (i_buf)
            print "============\n"
            self.do_help(self)
            
    def do_add(self, args):
        print item_id.values()
        print "Add what?"
        i_input = str.lower(raw_input())
        print i_input
        print "How many? (+/-)"
        qty = int(raw_input())
        print qty
        if party.items:
            for x in party.items:
                if str.lower(i_input) in str.lower(str(party.items.keys())):
                    party.items[x] += qty
        else:
            for x in item_id:
                print x 
                if str.lower(i_input) in str.lower(item_id[x].name):
                        party.items[str(item_id[x].name)] =+ qty

    def do_wander(self, args):
        roll = random.randrange(1,10,1)
        if roll >= 5:
            console = Battle()
            console.cmdloop()
        else:
            print "Found nothing...\n"
            time.sleep(1)

    def do_reset(self, args):
        print "Are you sure? (y/n)"
        x = raw_input()
        if x is "y":
            os.remove('./save/party_members.dat')
            os.remove('./save/party_gold.dat')
            os.remove('./save/party_items.dat')
            global party
            party = [] 
            tempparty = []
            tempparty += copy.deepcopy([human_id[1]])
            tempparty += copy.deepcopy([human_id[2]])
            tempparty += copy.deepcopy([human_id[3]])
            party = Party(3, tempparty)
            self.do_start(self)
        else:
            print "Party NOT reset."
            
    def do_fight(self, args):
        print '\x1b[1;1H\x1b[J'
        m_party_gen()
        global group 
        group = party.members + m_party.members
        print "A group consisting of %s appears!" % (m_party)
        turn = 0
        while (party.get_hp() > 0) and (m_party.get_hp() > 0):
            c = random.choice(group)
            if c.__class__.__name__ is "Mob":
            #0 = MOB ATTACKING/1 = HUMAN ATTACKING, ATTACKER, DEFENDER
                attack(0, c, random.choice(party.members), 0, 0)
                group.remove(c)
                if not group:
                    group = party.members + m_party.members
                    random.shuffle(group)
            elif c.__class__.__name__ is "Human":
                attack(1, c, random.choice(m_party.members), 0, 0)
                group.remove(c)
                if not group:
                    group = party.members + m_party.members
                    random.shuffle(group)
        if (party.get_hp() <= 0):
            print "Party\'s Over!"
        elif (m_party.get_hp() <= 0):
            totalxp = math.trunc(round(math.fsum([x.xp for x in m_party.members])))
            splitxp = math.trunc(round(totalxp / len(party.members)))
            party.set_xp(splitxp)
            print "Monster Party\'s Over!"
            lootbuffer = {}
            goldbuffer = 0
            for x in party.members:
                if x.xp >= x.xptn:
                    x.level_up()
            for x in m_party.members:
                lootchance = random.randrange(1,100,1)
                goldbuffer += x.gold
                if lootchance >= 50:
                    i_ran = item_id[random.choice(x.items)]
                    if not lootbuffer:
                        lootbuffer[str(i_ran)] = 1
                    else:
                        lootbuffer[str(i_ran)] += 1
            if lootbuffer:
                for each in lootbuffer:
                    if not party.items:
                        party.items[str(each)] = lootbuffer[each] 
                    else:
                        party.items[str(each)] += lootbuffer[each]
                party.gold += goldbuffer
                i_buf = ""
                for x in party.items:
                    i_buf += "%s x%d" % (x, lootbuffer[x])
                print "Party receives: %s and %d gold!" % ( i_buf, goldbuffer )
            if goldbuffer and not lootbuffer:
                party.gold += goldbuffer
                print "Party receives: %d gold!" % (goldbuffer)
        print "\n"
        self.do_help(self)
        return
        
    def do_summon(self, args):
        global party
        global summon
        if not summon:
            prevparty = copy.deepcopy([party])
            party = []
            party = Party(1, copy.deepcopy([summon_id[1]]))
        if summon:
            party = Party(3, prevparty)
        
    def do_use(self, args):
        if not party.items:
            print "You have no items!"
            return
        i_buf = ""
        for x in party.items:
            i_buf += "%s x%d" % (x, party.items[x])
        print "Items: %s" % (i_buf)
        print "Use which item?"
        i_in = raw_input()
        if str.lower(i_in) in str.lower(str(party.items)):
            print "OK!\n"
        elif str.lower(i_in) not in str.lower(str(party.items)):
            print "Item does not exist in your inventory!"
            return
        c_buf = ""
        for x in party.members:
            c_buf += x.name+", "
        if c_buf.endswith(', '):
            c_buf = c_buf[:-2]
        print c_buf
        print "On whom?"
        c_in = raw_input()
        i_id = 0
        c_id = 0
        if str.lower(c_in) not in str.lower(c_buf):
            print "Character does not exist in your party!"
            return
        if str.lower(i_in) in str.lower(str(party.items.keys())):
                for x in item_id:
                    if str.lower(i_in) in str.lower(item_id[x].name):
                        i_id = item_id[x].id 
        for index, x in enumerate(party.members):
            if c_in in x.name:
                c_id = index
        item_id[i_id].use(party.members[c_id])

    def do_rest(self, args):
        for x in party.members:
            x.hp = x.maxhp
            x.mp = x.maxmp
        print "Party's HP/MP is maxxed!"
        
    def do_mobs(self, args):
        pprint(mob_id.values())
        
    def do_cheat(self, args):
        for x in party.members:
            x.level_up()
        self.do_rest(self)
        print "Cheater!"
        
    def do_save(self, args):
        m = open('./save/party_members.dat', 'w+')
        i = open('./save/party_items.dat', 'w+')
        g = open('./save/party_gold.dat', 'w+')
        pickle.dump(party.members, m)
        pickle.dump(party.items, i)
        pickle.dump(party.gold, g)
        print "Saved!"
            
    def do_help(self, args):
        print "Commands: rename, status [party name/mob name], help, fight, rest, save, mobs, cheat, [exit/quit]"
            
    def default(self, line):
        self.do_help(self)
        

if __name__ == '__main__':
    console = Menu()
    console.cmdloop() 

# vim: sw=4 ts=4 expandtab
