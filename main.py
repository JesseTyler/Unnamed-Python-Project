#lolgit
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
#	 		How should I do turns? Variable, do the whole based on agi turn based system?
#			Or keep it as I have it by grouping all together and random.choice/popping?
#			Write new function with different situations to test alternatives?
#			
#			Add those new mobs, still gotta tweak with specific stats to make it more balanced.
#			[Done!/?] [Also, rewrite battles for generating the mob party to be within the average level of human
#			party within 2 or so levels.]
#
#			Also, add checks to see if mob has a healing spell, if so, cast whenever possible on
#			injured allies. Same with beneficial buffs such as haste and slow on enemies.
#
#			Add the aforementioned beneficial buffs!
#
#			Should I slim down the attack function and remove mob/human flags and do all the decision
#			making outside of the function (def think() for situations in entity class?)
#
#			Get those darned summons to work, was able to get the party to be replaced by Summoned
#			creature but, unable to replace party back into play.
#
#			Also try charging up/multi-phase spells such as Bomb's charge up and explode which
#			will kill a random party member, and setting up events defined in mobs initializations
#			using the s_flag/s_action parameters. (Check for better solution/Pre-Defined event
#			parties?)
#
#			Get equipment working, try only increasing one stat at first, maybe upping critical chance
#			by 2% while wearing, add check for attacker/defender's equipment enchantments
#
#			When tablet-get, draw some concept art for base human entities, thinking of doing a style
#			such as sorta cartoony mini-people, but with no mouths. Also, gotta do hats, bitches love hats.
#
#			Maybe also scarves, they get ladies too. Ascots!
#
#			Getting ahead of myself, though.
#
#			Worry about later: Story, Sounds, Final Art Style

import random, math, copy, time, cmd, pickle, os, re
from pprint import pprint

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
			#	setattr(self, n, v)
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
	
def attack(h_flag, attacker, defender, spell, ability):
	#attack(<Mob = 0, Human = 1>, attacker, defender)
	if attacker.get_hp() <= 0:
		return
	if h_flag is 0 and defender.get_hp() <= 0:
		defender = random.choice(party.members)
#Begin Mob Attack Section
	elif h_flag is 0 and defender.get_hp() > 0: 
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
				#print "Dmg: ", s_dmg
				s_crittotal = math.trunc(round(s_dmg * random.uniform(2,3)))
				#print "Crit: ", s_crittotal
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
		#print choice
		dodgecheck = (random.randint(1,100) + defender.agi - attacker.agi)
		orighp = defender.get_hp()
		if choice is spell and attacker.mp < choice.mpcost:
			print "%s tried casting %s but it fizzled!" % (attacker.name, choice.name)
		elif choice is spell and critcheck >= 8:
			if dodgecheck < 90:
				if math.trunc(round(defender.hp - round(s_crittotal - s_resist))) < 0:
					defender.set_hp(math.trunc(round(defender.get_hp() + round(s_crittotal - s_resist))))
					healed = math.trunc(round(defender.get_hp() - round(s_crittotal - s_resist))) 
					print "%s (%d) was healed by %s for %d with %s! %s is now at %d health!" % (defender.name, orighp, attacker.name, healed, spell_id[choice.id].name, defender.name, defender.get_hp())
				elif math.trunc(round(defender.hp - round(s_crittotal - s_resist))) >= 0:
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
				if math.trunc(round(defender.hp - round(s_dmg - s_resist))) < 0:
					healed = math.trunc(round(defender.get_hp() - round(s_dmg - s_resist))) 
					defender.set_hp(math.trunc(round(defender.get_hp() + round(s_dmg - s_resist))))
					print "%s (%d) was healed by %s for %d with %s! %s is now at %d health!" % (defender.name, orighp, attacker.name, healed, spell_id[choice.id].name, defender.name, defender.get_hp())
				elif math.trunc(round(defender.hp - round(s_dmg - s_resist))) >= 0:
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
					print "%s (%d) was hit by %s for %d (%d resisted) with %s! %s is now dead!" % (defender.name, orighp, attacker.name, (a_dmg + attacker.atk) - defender.arm, defender.arm, ability_id[choice.id].name, defender.name)
					defender.set_hp(0)
				elif defender.get_hp() > 0:
					print "%s (%d) was hit by %s for %d (%d resisted) with %s! %s is now at %d health!" % (defender.name, orighp, attacker.name, (a_dmg + attacker.atk) - defender.arm, defender.arm, ability_id[choice.id].name, defender.name, defender.get_hp())
			elif dodgecheck >= 90:
				print "%s attacks with %s... but %s dodged!" % (attacker.name, choice.name, defender.name) 
			return
#End Mob Attack
#Begin Human Attack
	if h_flag is 1 and defender.get_hp() <= 0:
		defender = random.choice(m_party.members)
	elif h_flag is 1 and defender.get_hp() > 0:
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
				#print "Dmg: ", s_dmg
				s_crittotal = math.trunc(round(s_dmg * random.uniform(2,3)))
				#print "Crit: ", s_crittotal
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
		#print choice
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
#Redundant/Unneeded? --v Check.
		if h_flag is 1 and defender.get_hp() <= 0:
			print attacker.name+" tries to attack but.. "+defender.name+" is dead!"
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
			
#Set up some default Mobs/Spells
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
		
#  - Spider, Goblin, Zombie, (Fire/Ice Wraith), Cobra, Bat, Toad, Bomb, Snake, Black Mamba, Moth, Imp, Slime, Bandit, Bandit Leader,
#    Box.
#			ID	NAME	  			LVL 	 HP    	XP     ARM     ATK     MP      MARM      AGI	 SPELLS			ABILITIES   Resistances [Fire, Water, Ice, Thunder, Arcane]		Gold		Items		Info
mob_1 = Mob(1,  "Rabbit", 			1, 	 	 10,  	6,     0,      2,      0,      0, 	  	 10,	 	 [],			[1,2], 				[5,    0,     5,   0,       0],			5,			[1],			"A small brown hare.")
mob_2 = Mob(2,  "Wolf",   			2, 		 20,  	10,    2,      5,      10,     0,    	 15,	     [],			[2], 				[0,    0,     0,   0,       0],			5,			[1],			"A battle-worn grey wolf.")
mob_3 = Mob(3,  "Spider", 			1,  	 15,    10,	   0,	   4,	   10,     0,		 12,		 [],			[2], 				[0,    0,     0,   0,       0],			5,			[1],			"A dog-sized poisonous spider.")
mob_4 = Mob(4,  "Cobra",  			2,   	 30,    15,    5,      6,      10,     0,        10,         [],			[2, 6], 			[0,    0,     0,   0,       0],			5,			[1],			"La paura del Cobra.")
mob_5 = Mob(5,  "Moth",				3,		 40,	20,	   3,	   5,	   10,	   5,		 13,		 [],			[6], 				[0,    0,     0,   0,       0],			5,			[1],			"A very hungry moth, aching of starvation for your robes.")
mob_6 = Mob(6,  "Imp",				3,		 45,	25,	   2,	   3,	   30,	   5,		 10,		 [1, 2],		[2], 				[0,    0,     0,   0,       0],			5,			[1],			"Can't we all justI get along?")
mob_7 = Mob(7,  "Toad",				3,		 50,	30,	   0,	   2,	   10,	   0,		 15,		 [],			[7], 				[0,    0,     0,   0,       0],			5,			[1],			"Ribbit.")
mob_8 = Mob(8,  "Ogre",   			10,  	 200, 	200,   10,     10,     10,     0,    	 5,	 		 [],			[3, 4, 5], 			[0,    0,     0,   0,       0],			5,			[1],			"Ogre, SMASH!")
mob_9 = Mob(9,  "Black Mamba",   	33,  	 200, 	1124,  24,     30,     0,      0,    	 50,	 	 [],			[8], 				[0,    0,     0,   0,       0],			5,			[1],			"Kobe!")

#				ID	NAME	  		LVL     HP       XP     ARM      ATK     MP      MARM    AGI	SPELLS		ABILITIES     Resistances [Fire, Water, Ice, Thunder, Arcane]
human_1 = Human(1,  "Fighter",    	1,   	20,   	 0,   	4,  	 2,  	 10,  	 0,    	 10,		[],		[4, 5], 				  [0,    0,     0,   0,       0])
human_2 = Human(2,  "Thief", 		1,   	20,   	 0,   	4,  	 2,  	 10,  	 0, 	 15,		[],		[4, 5], 				  [0,    0,     0,   0,       0])
human_3 = Human(3,  "Mage", 		1,   	20, 	 0,   	0,  	 0,  	 30,  	 0, 	 10,		[1, 2],	[], 					  [0,    0,     0,   0,       0])
#				  ID	NAME	  		LVL     HP       XP     ARM      ATK     MP      MARM    AGI	SPELLS		ABILITIES     Resistances [Fire, Water, Ice, Thunder, Arcane]
summon_1 = Summon(1,  	"Ifrit", 		10,   	250, 	 0,   	5,  	 15,  	 300,  	 0, 	 20,	[1, 2],		[], 					  [0,    0,     0,   0,       0])
#				ID	NAME		 			MP	 		MINDMG			MAXDMG		Type		Special Flag			Special Action
spell_1 = Spell(1,  "Fire Blast", 			6,  		6,				10,			"fire",		False,					0)
spell_2 = Spell(2,  "Ice Bolt", 			4,  		4,				8,			"ice",		False,					0)
spell_3 = Spell(3,  "Meteor",				25,			35,				50,			"fire",		False,					0)
#			  ID	NAME		Amount		Type
item_1 = Item(1, 	"Potion", 	20,			"heal_hp")
#					ID    NAME							MINDMG		    MAXDMG		Special Flag			Special Action
ability_1 = Ability(1,    "Rake", 		 				3,				5,			False,					0)
ability_2 = Ability(2,    "Bite", 		 				5,				7,			False,					0)
ability_3 = Ability(3,    "Crush",						20,				25,			False,					0)
ability_4 = Ability(4,    "Kick",						6,				9,			False,					0)
ability_5 = Ability(5,    "Punch",						5,				7,			False,					0)
ability_6 = Ability(6,    "Poison Fang",				8,				10,			False,					0)
ability_7 = Ability(7,	  "Croak",						0,				0,			True,					"print \"Toad croaks.\"")
ability_8 = Ability(8,	  "Fang Dunk",					25,				50,			False,					0)

#Define Predetermined Mob Parties
mob_p1 = [copy.deepcopy(mob_id[1])]	
mob_p2 = [copy.deepcopy(mob_id[1]), copy.deepcopy(mob_id[1])]
mob_p3 = [copy.deepcopy(mob_id[1]), copy.deepcopy(mob_id[1]), copy.deepcopy(mob_id[1])]

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
				print x.name+" ("+x.job+")\n"+"	| Level:", x.lvl, "| HP:", x.hp, "| MP:", x.mp, "| Xp:", x.xp, "| Xp till Level:", x.xptn - x.xp, "| Status:", status_buf
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
				print x.name+"\n"+"	| Level:", x.lvl, "| HP:", x.hp, "| MP:", x.mp, "| Status:", status_buf
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
				sleep(2)
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
	tempparty += copy.deepcopy([human_id[1]])
	tempparty += copy.deepcopy([human_id[2]])
	tempparty += copy.deepcopy([human_id[3]])
	party = Party(3, tempparty)
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
			print x.name+" ("+x.job+")"+"	| Level:", x.lvl, "| HP:", x.hp, "| MP:", x.mp
		print "============\n"
		self.do_save(self)
			
	def do_rename(self, args):
		print '\x1b[1;1H\x1b[J'
		for x in party.members:
			print "Name your", x.job+": "
			x.name = raw_input()
		print "\n"
		for x in party.members:
			print x.name+" ("+x.job+")"+"	| Level:", x.lvl, "| HP:", x.hp, "| MP:", x.mp

#	def do_status(self, args):
#		print '\x1b[1;1H\x1b[J'
#		if re.match("^[A-Za-z0-9]", str(args)):
#			for x in party.members:
#				if str.lower(x.name) in str.lower(str(args)):
#					print "============"
#					x.get_status()
#					print "============\n"
#					return
#			for x in mob_id:
#				if str.lower(mob_id[x].name) in str.lower(str(args)):
#					print "============"
#					mob_id[x].get_status()
#					print "============\n"
#					return

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
				print x.name+" ("+x.job+")\n"+"	| Level:", x.lvl, "| HP:", x.hp, "| MP:", x.mp, "| Xp:", x.xp, "| Xp till Level:", x.xptn - x.xp
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
