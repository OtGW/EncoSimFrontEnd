from datetime import datetime
import numpy as np
from random import random, shuffle
import json
import os
import sys
from functools import partial
from copy import copy


#Simulator
def fight_ongoing_check(fight): #this function takes the fighters and checks if more then one team is still alive
    fighter_tag_list = []
    for i in range(0, len(fight)):
        if fight[i].CHP > 0 and fight[i].team not in fighter_tag_list:
            fighter_tag_list.append(fight[i].team)
    if len(fighter_tag_list) > 1:
        return True
    else:
        return False

def do_the_fighting(fighters_unsorted): #here a list of fighters from different teams
    fight = roll_for_initiative(fighters_unsorted)     #roll all inits and return sorted list
    Init_counter = 0
    DM = fighters_unsorted[0].DM
    DM.reset() #resets the DM at start of fighting

    DM.say('Runde ' + str(DM.rounds_number) + ' - Heros Teamhealth: ' + str(teamhealth(fight, 0)), True)

    while fight_ongoing_check(fight) == True:
        player = fight[Init_counter]

        if player.state != -1:
            DM.say('_____________', True)
        if player.state == 1:                            #player is alive
            enemies_left_list = [x for x in fight if x.team != player.team and x.state == 1]

            player.start_of_turn()

            if enemies_left_list != []:   #if enemies left, call an AI for the turn    
                player.AI.do_your_turn(fight)

        #if player is dead, make death save
        if player.state == 0 and player.team == 0:
            player.make_death_save()

        #End of the Turn
        player.end_of_turn()   #after turn, reset counter, haste, stuff, all that happends at end of turn

        Init_counter += 1                                #set Init counter, reset round counter if ness.
        if Init_counter >= len(fight):
            Init_counter = 0
            DM.rounds_number += 1
            DM.say('', True)
            DM.say('Runde ' + str(DM.rounds_number) + ' - Heros Teamhealth: ' + str(teamhealth(fight, 0)), True)


    #Only one Team is left alive
    DM.say('', True)
    DM.say("Fight over", True)
    for x in fighters_unsorted:
        if x.CHP == 0:
            x.state = -1 #Everone who is unconscious in the loser Team is practically Dead now
        if x.is_summoned:  #let summend characters vanish after dead
            fight.remove(x)
        x.TM.resolveAll()
        

    DM.say('HP left:', True)
    for i in fighters_unsorted:
        DM.say(str(i.name) + " " + str(i.CHP), True)
    DM.say('', True)
    DM.say('Damage dealed:', True)
    for i in fighters_unsorted:
        DM.say(str(i.name) + " " + str(round(i.dmg_dealed,2)), True)
    DM.say('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', True)
    DM.say('XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX', True)
    DM.say('', True)
    DM.say('', True)
    
    winner_team = 0
    for i in fighters_unsorted:
        if i.CHP > 0:
            winner_team = i.team
            break
    
    return winner_team, DM.rounds_number

#all statistical functions call this one and this one calls the 'do the fighting'
#for multiple fightings, change here

def roll_for_initiative(fighters_unsorted): #takes list of fighters and return init order
    for i in fighters_unsorted:
        i.initiative = i.make_check(1)   #make Dex roll
    initiative = sorted(fighters_unsorted, reverse = True, key=lambda x: x.initiative)
            #roll all inits and return sorted list
    return initiative

def enemies_left_sort(fight, TeamTag):
    enemies_left_list = [x for x in fight if x.team != TeamTag and x.state == 1]
    return enemies_left_list

def run_simulation(repetition, fighters, progress = False):
    damage_statistic = []
    winner = []
    rounds_number = []
    deaths = []
    unconscious = []
    DeathNumber = np.zeros(repetition)#Counts the absolute Deaths per Repetition (only for team 0)
    TeamHealth = [] #List with how much of the absolute Team Health is left
    TeamHP = 0
    for fighter in fighters:
        if fighter.team == 0:
            TeamHP += fighter.HP

    for i in range(0,repetition):
        percent = str(round(i/repetition*100, 1))
        progress = 'Progress : ' + percent + '%'
        # if progress == True:
        #     print('Progress : ' + percent +'%')


        simulation_results = do_the_fighting(fighters)
        winner.append(simulation_results[0])         # do the fight and get the winner, list of 0 (heros) or 1 (enemies)
        rounds_number.append(simulation_results[1])         # do the fight and get the rounds number
        damage_statistic.append([k.dmg_dealed for k in fighters])  #get dmg statistic

        for j in fighters:
            if j.state == -1:
                deaths.append(j.name)
                if j.team == 0:
                    DeathNumber[i] += 1 #Counts the absolute Deaths per Repetition
        
        TeamCHP = 0
        for fighter in fighters:
            if fighter.team == 0:
                TeamCHP += fighter.CHP
        TeamHealth.append(TeamCHP/TeamHP) #how much Team health is left

        UnconsciousSum = 0
        for j in fighters:
            if j.team == 0:
                UnconsciousSum += j.unconscious_counter
        unconscious.append(UnconsciousSum)
        
        for l in fighters:
            l.long_rest()           #rest by doing a long Rest
    damage_statistic_sorted = []
    for j in range(0, len(fighters)):          #sort dmg statistic
        damage_statistic_sorted.append([damage_statistic[i][j] for i in range(0,repetition)])
    names = [i.name for i in fighters]         #get names 

    return names, damage_statistic_sorted, winner, rounds_number, deaths, unconscious, DeathNumber, TeamHealth

def most_valuable_player(repetition, fighters):
    DM = fighters[0].DM
    Heros_List = [fighter for fighter in fighters if fighter.team == 0]
    if len(Heros_List) == 1: # if only one Heros is in the team
        return [[Heros_List[0].name], [0], Heros_List[0].name]
    fighters_without_one_hero = copy(fighters)
    player_name = []
    win_probability_without_player = []
    for i in range(0, len(fighters_without_one_hero)):
        if fighters_without_one_hero[i].team == 0:
            fighters_without_one_hero.remove(fighters[i])
            player_name.append(fighters[i].name) 
            names, damage_statistic_sorted, winner, rounds_number, deaths, unconscious, DeathNumber, TeamHealth = run_simulation(repetition, fighters_without_one_hero)
            
            #calc win prob.
            wins = 0
            defeats = 0
            for i in winner:
                if i == 0:
                    wins += 1
                else:
                    defeats += 1
            win_probability = wins/(wins + defeats)
            win_probability_without_player.append(win_probability)

            DM.say('Win Probability = ' + str(win_probability) + '\n', True)
            fighters_without_one_hero = copy(fighters)
    
    mvp_index = argmin(win_probability_without_player)
    DM.say('Most valuable player: ' + str(player_name[mvp_index]), True)
    return player_name, win_probability_without_player, player_name[mvp_index]

def spell_cast_recap(repetition, fighters, text_result):  #only calls the objects data, simulation must be run beforehand
    for fighter in fighters:
        if len(fighter.SpellBook) > 0:
            for spell_name, spell in fighter.SpellBook.items():
                if spell.was_cast > 0:
                    text_result += str(fighter.name) + ' cast ' + spell.spell_text + ': ' + str(round(spell.was_cast/repetition,3)) + '\n'
    return text_result

def full_statistical_recap(repetition, fighters):
    DM = fighters[0].DM
    DM.start_time = datetime.now()

    #generate a str that will be returned
    text_result = 'Simulation estimates:\n'

    #run simulation
    names, damage_statistic_sorted, winner, rounds_number, deaths, unconscious, DeathNumber, TeamHealth = run_simulation(repetition, fighters, progress=True)
    wins = 0
    defeats = 0
    for i in winner:
        if i == 0:
            wins += 1
        else:
            defeats += 1
    win_probability = wins/(wins + defeats)

    # run the most valuable player function with less repetitions
    #This section was removed due to high performance impact
    if False:
        DM.block_print()
        mvp_repetitions = int(repetition/10) +1
        if mvp_repetitions > 100:
            mvp_repetitions = 100
        player_name, win_probability_without_player, mvp = most_valuable_player(mvp_repetitions, fighters)
        DM.enable_print()


    # Calaculate death rates  (if they loose, they all die obviously)
    DeathProbabilities = []
    Deaths_text_result = ''
    for i in fighters:
        if i.team != 1:
            fighter_has_died_counter = 0   #death counter
            for j in deaths:
                if i.name == j:   #if name is in deaths from simulation
                    fighter_has_died_counter += 1
            if fighter_has_died_counter > 0:
                death_probability = fighter_has_died_counter/repetition
                Deaths_text_result += str(i.name) + ' dies: ' + str(round(death_probability*100,2)) + ' %\n'
            else:
                death_probability = 0
            DeathProbabilities.append(death_probability) # for late calc difficulty

    #Calculate the Difficulty
    Difficulty = calculate_difficulty(1-win_probability, np.mean(rounds_number), DeathProbabilities, unconscious, DeathNumber, TeamHealth)
    Difficulty_Text = ['0',
    'Insignificant', 'Easy', 'Medium', 'Challenging', 'Hard',
    'Brutal', 'Insane', 'Death', 'Hell', 'How Dare You?']

    Difficulty_Meaning = ['0',
    'No chance of failure and the heroes will still have most of their recources',
    'A low risk fight, that will leave but a scratch.',
    'This might take some efford. Death will only come to those who take it lightly.',
    'Finally, a worthy fight that will force the heroes to show what they are made of.',
    'Death is a real danger now, fatal for those how are not prepared.',
    'Some might not survive this fight, it is deadly and unforgiving.',
    'This is madness and could bring death to all. Be cautious.',
    'A total annihilation is likely. If some survive, at what cost?',
    'Burn them all. The gods must have forsaken these poor heroes.',
    'What are you thinking? You must hate them...'
    ]

    damage_player = [np.mean(damage_statistic_sorted[i]) for i in range(0, len(damage_statistic_sorted))]

    text_result += '_____________________\n'
    text_result += 'Difficulty: ' + Difficulty_Text[Difficulty] + '\n'
    text_result += 'Win Probability: ' + str(round(win_probability*100, 3)) + ' %\n'
    text_result += 'Fight Length: ' + str(round(np.mean(rounds_number),1)) + ' +/- ' + str(round(np.std(rounds_number),1)) + '\n'
    text_result += 'Team Health: ' + str(round(np.mean(TeamHealth)*100,1)) + ' %\n'
    text_result += 'Total Party Kill: ' + str(round((1-win_probability)*100, 3)) + ' %\n\n'
    text_result += Difficulty_Meaning[Difficulty] + '\n\n'
    text_result += '----DEATHS----\n'
    text_result += Deaths_text_result
    text_result += '\n'
    if win_probability > 0.01:
        text_result += '----PLAYER PERFORMANCE----\n'

    #calculating the performance of the Players
        #Perfprmance as the part of Dmg done:
        player = [x for x in fighters if x.team == 0]
        damage_list = []
        for i in range(0, len(fighters)):
            if fighters[i].team == 0:
                damage_list.append(damage_player[i])
        performance_damage = np.zeros(len(damage_list))
        for i in range(0, len(performance_damage)):
            performance_damage[i] = damage_list[i]/np.max(damage_list)
        for i in range(0,len(player)):
            text_result += str(player[i].name) + ' : ' + str(int(100*performance_damage[i])) + '/100 \n'

    text_result += '\n'
    text_result += '----DAMAGE DONE----\n'
    for i in range(0,len(fighters)):
        text_result += fighters[i].name + ' : ' + str(int(damage_player[i])) + '\n'
    text_result += '\n'
    text_result += '----SPELLS CAST----\n'
    text_result = spell_cast_recap(repetition, fighters, text_result)


    return text_result

def calculate_difficulty(TPKChance, Length, DeathProbabilities, Unconscious, DeathNumber, TeamHealth):
    #TPK Chance = 1 - Winchance 
    #Length of fight
    #Deathprob List of Death chances 
    #Unconscious Counters List
    #Death Number is absolute Deaths per Simulation
    #TeamHealth is list with how much of the total team CHP was left per run
    #This function tries to estimate how difficult the encounter would be
    #1 - Insignificant, no chance of fail
    #2 - Easy, no death chance, easy fight    
    #3 - Medium, will take some efford, minimal death chance
    #4 - Challenging, some fight, chane of fail, flee maybe
    #5 - Hard, will take efford, chance of death
    #6 - Brutal, will propably lead to some deaths, maybe TPK
    #7 - Insane, real chance of TPK
    #8 - Death, a TPK is likely
    #9 - Hell, a TPK is highly likely
    #10 - How Dare You, just what were you thinking?
    DeathPerPlayer = sum(DeathProbabilities)/len(DeathProbabilities)
    MinDeaths = np.mean(np.sort(DeathNumber)[0:int(len(DeathNumber)/20+1)]) #lowest 5%
    MinUnconscious = np.mean(np.sort(Unconscious)[0:int(len(Unconscious)/20+1)]) #lowest 5%
    MeanTeamHealth = np.mean(TeamHealth)

    #HowDareYou
    if TPKChance > 0.9 and MinDeaths > 1:
        return 10 #This is a 90% TPK
    #Hell
    elif TPKChance > 0.75 and DeathPerPlayer > 0.85 and MinDeaths > 1:
        return 9 #This is likely TPK and at least 2 player die in any run
    #Death
    elif TPKChance > 0.5 and DeathPerPlayer > 0.6:
        return 8 #50% TPK, at least one Player dies in any run
    else:
        #TPKChance>, Length>, >DeathPerPlayer MinDeath>, MinUncon>, MeanTeamHealth<
        lv1 = [0.005, 3, 0.01, 0, 0.5, 0.8]
        lv2 = [0.01, 5, 0.03, 0.1, 2, 0.7]
        lv3 = [0.02, 7, 0.15, 0.5, 4, 0.5]
        lv4 = [0.05, 10, 0.25, 1, 5, 0.3]
        lv5 = [0.2, 15, 0.33, 2, 10, 0.1]
        lv6 = [0.3, 20, 0.4, 2.5, 20, 0.05]
        Level = [lv1,lv2, lv3, lv4, lv5, lv6]
        Diff = 0
        while Diff < 6: #Is right, because Diff starts at 0
            #This Loop iterates the Boundries of the Level
            #If one Value is higher then the Boundry, the Difficulty Level is risen
            #else the current Diff is returned
            if TPKChance > Level[Diff][0]:
                Diff +=1
            elif Length > Level[Diff][1]:
                Diff +=1
            elif DeathPerPlayer > Level[Diff][2]:
                Diff +=1
            elif MinDeaths > Level[Diff][3]:
                Diff +=1
            elif MinUnconscious > Level[Diff][4]:
                Diff +=1
            elif MeanTeamHealth < Level[Diff][5]:
                Diff +=1
            else:
                return Diff + 1 #Diff starts with 0, but is 1
        return 7
        
def teamhealth(fight, teamtag):
    healthlist = []
    for i in range(0, len(fight)):                  #sort team
        if fight[i].team == teamtag and fight[i].CHP > 0:
            healthlist.append(fight[i].CHP)
    return sum(healthlist)


class DungeonMaster:
    def __init__(self):
        self.AI_blank = False #just ignore, but MUST be False, see AI Class
        self.printing_on = False
        self.start_time = datetime.now()


        self.density = 1
        #density: 0 - loose, 1 - normal, 2 - dense
        self.rounds_number = 1

        self.text = ''

    def reset(self):
        #This function is called a the start of the fighting and resets the DM
        self.rounds_number = 1
    
    def block_print(self):
        self.printing_on = False

    def enable_print(self):
        self.printing_on = True

    def say(self, text_to_say, this_is_new_line=False):
        if self.printing_on:
            if False:                       #This is a hard coded, disabled developer Function 
                if False:#total diff in ms
                    print(str(round((datetime.now() - self.start_time).total_seconds()*1000, 3)), end=': ')
                if True:#diff to last 
                    print(str(round((datetime.now() - self.start_time).total_seconds()*1000, 3)), end=': ')
                    self.start_time = datetime.now()
            if this_is_new_line:
                print(self.text)
                self.text = '' #start new line
            self.text = ''.join([self.text, text_to_say])

class entity:                                          #A Character
    def __init__(self, name, team, DM, archive = False, external_json = False):                  #Atk - Attack [+x to Hit, mean dmg]

        if external_json == False:
            file = open(path)
            data = json.load(file)
            file.close()
        else:
            data = external_json


        self.data = data
        self.DM = DM
        self.TM = TokenManager(self)  #Token Manager

    #Base Properties
        self.name = str(name)
        self.orignial_name = str(name)        #restore name after zB WildShape
        self.team = team                                      #which Team they fight for
        self.type = str(data['Type'])
        self.base_type = self.type

        self.AC = int(data['AC'])         #Current AC that will be called, and reset at start of turn
        self.shape_AC =int(data['AC'])     #AC of the current form, changed by wild shape
        self.base_AC = int(data['AC'])      #AC of initial form, will be set to this after reshape
        self.HP = int(data['HP'])
        self.proficiency = int(data['Proficiency'])
        self.tohit = int(data['To_Hit'])
        self.base_tohit = int(data['To_Hit'])

        self.base_attacks = int(data['Attacks'])    #attacks of original form   #number auf Attacks
        self.attacks = self.base_attacks  #at end_of_turn attack_counter reset to self.attack
        self.dmg = float(data['DMG'])           #dmg per attack
        self.base_dmg = float(data['DMG'])
        self.offhand_dmg = float(data['OffHand']) #If 0, no Offhand dmg

        self.level = float(data['Level'])           #It is not fully implementet yet, but level is used in some functions already, Level is used as CR for wildshape and co
        try: self.strategy_level = int(data['StrategyLevel']) #Value 1-10, how strategig a player is, 10 means min. randomness
        except: self.strategy_level = 5 #Medium startegy
        if self.strategy_level < 1: self.strategy_level = 1
        if self.strategy_level > 10: self.strategy_level = 10

        #Calculate Random Weight, for target_attack_score function
        #random factor between 1 and the RandomWeight
        #Random Weight of 0 is no random, should not be 
        #Random Weight around 2 is average 
        self.random_weight = 38.4/(self.strategy_level+2.47)-2.95

    #Position management
        self.speed = int(data['Speed'])
        #positions: 0 - front line, 1 - mid, 2 - back line
        self.position_txt = data['Position'] #front is default
        self.base_position = 0
        if 'middle' in self.position_txt:
            self.base_position = 1
        elif 'back' in self.position_txt:
            self.base_position = 2
        self.position = self.base_position  #This position will be called
        # airborn = 3 for player who can fly
        #Can the Character use range attacks
        self.range_attack = int(data['Range_Attack'])
        if self.range_attack == 1:
            self.has_range_attack = True
        else:
            self.has_range_attack = False

    #Abilities and Stats    
        self.Str = int(data['Str'])
        self.Dex = int(data['Dex'])
        self.Con = int(data['Con'])
        self.Int = int(data['Int'])
        self.Wis = int(data['Wis'])
        self.Cha = int(data['Cha'])
        self.stats_list = [self.Str, self.Dex, self.Con, self.Int, self.Wis, self.Cha]       #used for temp changes and request
        self.base_stats_list = self.stats_list
        self.modifier = [round((self.stats_list[i] -10)/2 -0.1, 0) for i in range(0,6)]  #calculate the mod
        self.base_modifier = self.modifier

        #actually only the modifier are currently ever used
        self.saves_prof = data['Saves_Proficiency']        #Already in Entity, not implementet in fight functions tho
        #list for saves of all kind. if = 0, no advantage 
        #if > 0 has advantage
        #if < 0 has disadvantage
        self.HeroVillain = int(data['Hero_or_Villain'])

    #Damage Types
        self.damage_type = data['Damage_Type']
        self.base_damage_type = self.damage_type
        self.damage_resistances = data['Damage_Resistance']
        self.base_damage_resistamces = self.damage_resistances
        self.damage_immunity = data['Damage_Immunity']
        self.base_damage_immunity = self.damage_immunity
        self.damage_vulnerability = data['Damage_Vulnerabilities']
        self.base_damage_vulnerability = self.damage_vulnerability

        self.additional_resistances = ''     #for rage and stuff

        self.last_used_DMG_Type = data['Damage_Type']

    #Spellcasting
        self.spell_mod = int(data['Spell_Mod'])                    #spell modifier
        self.spell_dc = int(data['Spell_DC'])                                #spell save DC

        self.spell_slots = [int(data['Spell_Slot_' + str(i)]) for i in range(1,10)]  #fixed spell slots available ( 0 - Level1, 1 - Level2, ...)
        self.spell_slot_counter = [int(data['Spell_Slot_' + str(i)]) for i in range(1,10)] #current counter for used spell slots 

        #Spells known
        self.spell_list = data['Spell_List']

        #If this updates, the All_Spells in the GUI will load this
        #Keep this in Order of the Spell Level, so that it also fits for the GUI
        self.SpellNames = ['FireBolt', 'ChillTouch', 'EldritchBlast',
                           'BurningHands', 'MagicMissile', 'GuidingBolt', 'Entangle', 'CureWounds', 'HealingWord', 'Hex', 'ArmorOfAgathys', 'FalseLife', 'Shield', 'InflictWounds', 'HuntersMark',
                           'AganazzarsSorcher', 'ScorchingRay', 'Shatter', 'SpiritualWeapon',
                           'Fireball', 'LightningBolt', 'Haste', 'ConjureAnimals', 'CallLightning',
                           'Blight', 'SickeningRadiance', 'WallOfFire', 'Polymorph',
                           'Cloudkill']
        #Add here all Spell classes that are impemented
        self.Spell_classes = [firebolt, chill_touch, eldritch_blast,
                         burning_hands, magic_missile, guiding_bolt, entangle, cure_wounds, healing_word, hex, armor_of_agathys, false_life, shield, inflict_wounds, hunters_mark,
                         aganazzars_sorcher, scorching_ray, shatter, spiritual_weapon,
                         fireball, lightningBolt, haste, conjure_animals, call_lightning,
                         blight, sickeningRadiance, wallOfFire, polymorph,
                         cloudkill]
        #A Spell Class will only be added to the spellbook, if the Spell name is in self.spell_list
        self.SpellBook = dict()
        for x in self.Spell_classes:
            spell_to_lern = x(self)  #Initiate Spell
            if spell_to_lern.is_known: #If Spell is known, append to SpellBook
                self.SpellBook[spell_to_lern.spell_name] = spell_to_lern

        #Haste
        self.is_hasted = False
        self.haste_round_counter = 0    #when this counter hits 10, haste will wear off
        #Hex 
        self.is_hexed = False
        self.is_hexing = False
        self.can_choose_new_hex = False 
        self.CurrentHexToken = False #This is the Hex Concentration Token
        #Hunters Mark
        self.is_hunters_marked = False
        self.is_hunters_marking = False
        self.can_choose_new_hunters_mark = False 
        self.CurrentHuntersMarkToken = False #This is the Hunters Mark Concentration Token
        #Armor of Agathys
        self.has_armor_of_agathys = False
        self.agathys_dmg = 0
        #Spiritual Weapon
        self.has_spiritual_weapon = False
        self.SpiritualWeaponDmg = 0
        self.SpiritualWeaponCounter = 0
        #Conjure Animals
        self.is_summoned = False       #if True it will be removed from fight after dead
        self.summoner = False      #general for all summoned entities
        self.has_summons = False
        #Guiding Bolt
        self.is_guiding_bolted = False
        #Chill Touch
        self.chill_touched = False
        #Cloudkill
        self.is_cloud_killing = False
        #sickening radiance
        self.is_using_sickening_radiance = False



    #Special Abilities
        self.other_abilities = data['Other_Abilities']
        #Action Surge
        if 'ActionSurge' in self.other_abilities:
            self.knows_action_surge = True
        else: self.knows_action_surge = False
        self.action_surges = int(data['ActionSurges'])       #The base how many action surge the player has
        self.action_surge_counter = self.action_surges
        self.action_surge_used = False
        #Improved Critical
        if 'ImprovedCritical' in self.other_abilities:
            self.knows_improved_critical = True
        else:self.knows_improved_critical = False
        #Second Wind
        if 'SecondWind' in self.other_abilities:
            self.knows_second_wind = True
        else:
            self.knows_second_wind = False
        self.has_used_second_wind = False

        #Archery
        if 'Archery' in self.other_abilities:
            self.knows_archery = True
        else: self.knows_archery = False
        #Great Weapon Fighting
        if 'GreatWeaponFighting' in self.other_abilities:
            self.knows_great_weapon_fighting = True
        else: self.knows_great_weapon_fighting = False
        #Interception
        if 'Interception' in self.other_abilities:
            self.knows_interception = True
        else: self.knows_interception = False
        self.interception_amount = 0 #is true if a interceptor is close, see end_of_turn

        #UncannyDodge
        if 'UncannyDodge' in self.other_abilities:
            self.knows_uncanny_dodge = True
        else:
            self.knows_uncanny_dodge = False
        #Cunning Action
        self.knows_cunning_action = False
        if 'CunningAction' in self.other_abilities:
            self.knows_cunning_action = True
        #Wails from the Grave
        self.wailsfromthegrave = 0
        self.wailsfromthegrave_counter = self.proficiency
        if 'WailsFromTheGrave' in self.other_abilities:
            self.wailsfromthegrave = 1    #is checked in Attack Function, wails from the grave adds just ot sneak attack at the moment, improvement maybe?
        #Sneak Attack
        self.sneak_attack_dmg = float(data['Sneak_Attack_Dmg'])        #If Sneak_Attack is larger then 0, the Entity has sneak Attack
        self.sneak_attack_counter = 1                  #set 0 after sneak attack     
        #Assassinate
        self.knows_assassinate = False
        if 'Assassinate' in self.other_abilities:
            self.knows_assassinate = True

        #RecklessAttack
        self.knows_reckless_attack = False
        if 'RecklessAttack' in self.other_abilities:
            self.knows_reckless_attack = True
        self.reckless = 0    #while reckless, u have ad but attacks against u have too, must be called in Player AI
        #Rage
        self.knows_rage = False
        self.rage_dmg = 0
        if 'Rage' in self.other_abilities:
            self.knows_rage = True
            self.rage_dmg = float(data['RageDmg'])
        self.raged = 0     # 1 if currently raging
        self.rage_round_counter = 0
        #Frenzy
        self.knows_frenzy = False
        if 'Frenzy' in self.other_abilities:
            self.knows_frenzy = True
        self.is_in_frenzy = False
        if 'BearTotem' in self.other_abilities:
            self.knows_bear_totem = True
        else:
            self.knows_bear_totem = False
        if 'EagleTotem' in self.other_abilities:
            self.knows_eagle_totem = True
        else:
            self.knows_eagle_totem = False
        if 'WolfTotem' in self.other_abilities:
            self.knows_wolf_totem = True
        else:
            self.knows_wolf_totem = False
        self.has_wolf_mark = False #Is true if you were attacked last by a Totel of the Wolf barbarian
        
        #Lay On Hands
        self.lay_on_hands = int(data['Lay_on_Hands_Pool'])            #pool of lay on hands pool
        self.lay_on_hands_counter = self.lay_on_hands    #lay on hands pool left
        #Smite
        self.knows_smite = False
        if 'Smite' in self.other_abilities:
            self.knows_smite = True
        #Aura of Protection
        self.knows_aura_of_protection = False
        if 'AuraOfProtection' in self.other_abilities:
            self.knows_aura_of_protection = True
            #Is implemented in the do_your_turn function via area of effect chooser

        #Inspiration
        if 'Inspiration' in self.other_abilities:
            self.knows_inspiration = True
            self.inspiration_die = int(data['Inspiration'])
            if self.inspiration_die not in [0,2,3,4,5,6]:
                self.inspiration_die = 0
        else:
            self.knows_inspiration = False
            self.inspiration_die = 0
        self.inspired = 0   #here the amount a target is inspired
        if self.modifier[5] > 0: self.base_inspirations = self.modifier[5]
        else: self.base_inspirations = 1
        self.inspiration_counter = self.base_inspirations     #for baric inspiration char mod
        #Combat Inspiration
        if 'CombatInspiration' in self.other_abilities:
            self.knows_combat_inspiration = True
        else: self.knows_combat_inspiration = False
        self.is_combat_inspired = False 
        if 'CuttingWords' in self.other_abilities:
            self.knows_cutting_words = True
        else: self.knows_cutting_words = False

        #ChannelDevinity
        self.channel_divinity_counter = int(data['ChannelDivinity'])
        if self.channel_divinity_counter > 0:
            self.knows_channel_divinity = True
        else:
            self.knows_channel_divinity = False
        #Turn Undead
        if 'TurnUndead' in self.other_abilities:
            self.knows_turn_undead = True
        else:
            self.knows_turn_undead = False
        self.is_a_turned_undead = False
        self.turned_undead_round_counter = 0
        #DestroyUndead
        self.destroy_undead_CR = float(data['DestroyUndeadCR'])

        #Agonizing Blast
        self.knows_agonizing_blast = False
        if 'AgonizingBlast' in self.other_abilities:
            self.knows_agonizing_blast = True

        #Primal Companion
        try: self.favored_foe_dmg = float(data['FavoredFoeDmg'])
        except: self.favored_foe_dmg = 0
        self.knows_favored_foe = False
        self.favored_foe_counter = self.proficiency
        self.has_favored_foe = False
        if self.favored_foe_dmg > 0: self.knows_favored_foe = True
        self.knows_primal_companion = False
        self.used_primal_companion = False  #only use once per fight
        if 'PrimalCompanion' in self.other_abilities:
            self.knows_primal_companion = True
        self.primal_companion = False 
        self.knows_beastial_fury = False
        if 'BestialFury' in self.other_abilities:
            self.knows_beastial_fury = True

    #Feats
        #Great Weapon Master
        self.knows_great_weapon_master = False
        if 'GreatWeaponMaster' in self.other_abilities:
            self.knows_great_weapon_master = True
        self.has_additional_great_weapon_attack = False
        self.knows_polearm_master = False
        if 'PolearmMaster' in self.other_abilities:
            self.knows_polearm_master = True
            poleArmDMG = 2.5 + max(self.base_modifier[0], self.base_modifier[1]) #Dex or Str
            if self.offhand_dmg < poleArmDMG:
                self.offhand_dmg = poleArmDMG #1d4 + attack mod

    #Meta Magic
        self.sorcery_points_base = int(data['Sorcery_Points'])
        self.sorcery_points = self.sorcery_points_base
        self.knows_quickened_spell = False
        if 'QuickenedSpell' in self.other_abilities:
            self.knows_quickened_spell = True
        self.quickened_spell = 0  #if 1 a Action Spell will be casted as BA, can be called as via quickened Spell function from spell class
        self.knows_empowered_spell = False
        if 'EmpoweredSpell' in self.other_abilities:
            self.knows_empowered_spell = True
        self.empowered_spell = False #if True, the next Spell will ne empowered (20% mehr dmg)
        self.knows_twinned_spell = False
        if 'TwinnedSpell' in self.other_abilities:
            self.knows_twinned_spell = True

    # Ki Points
        try: self.ki_points_base = int(data['Ki_Points'])
        except: self.ki_points_base = 0
        self.ki_points = self.ki_points_base
        self.ki_save_dc = 8 + self.proficiency + self.modifier[4]
        self.knows_deflect_missiles = False
        if 'DeflectMissiles' in self.other_abilities:
            self.knows_deflect_missiles = True
        self.knows_flurry_of_blows = False
        if 'FlurryOfBlows' in self.other_abilities:
            self.knows_flurry_of_blows = True
        self.knows_patient_defense = False
        if 'PatientDefense' in self.other_abilities:
            self.knows_patient_defense = True
        self.knows_step_of_the_wind = False
        if 'StepOfTheWind' in self.other_abilities:
            self.knows_step_of_the_wind = True
        self.knows_stunning_strike = False
        if 'StunningStrike' in self.other_abilities:
            self.knows_stunning_strike = True
        self.knows_open_hand_technique = False
        if 'OpenHandTechnique' in self.other_abilities:
            self.knows_open_hand_technique = True

    #Monster Abilites
        self.knows_dragons_breath = False
        if 'DragonsBreath' in self.other_abilities:
            self.knows_dragons_breath = True
        self.knows_spider_web = False
        if 'SpiderWeb' in self.other_abilities:
            self.knows_spider_web = True
        self.knows_poison_bite = False
        self.poison_bites = 1         #Only once per turn
        self.poison_bite_dmg = 0      #dmg of poison bite
        self.poison_bite_dc = 0
        if 'PoisonBite' in self.other_abilities:
            self.knows_poison_bite = True
            #Dmg roughly scales with Level
            self.poison_bite_dmg = 8 + self.level*3
            self.poison_bite_dc = int(11.1 + self.level/3)
        
        self.knows_recharge_aoe = False
        if 'RechargeAOE' in self.other_abilities:
            self.knows_recharge_aoe = True

        try: self.aoe_recharge_dmg = data['AOERechargeDmg']
        except: self.aoe_recharge_dmg = 0
        try: self.aoe_recharge_dc = int(data['AOERechargeDC'])
        except: self.aoe_recharge_dc = 0
        try: self.aoe_save_type = int(data['AOESaveType']) #0 - Str, 1 - Dex, ...
        except: self.aoe_save_type = 0
        try: self.aoe_recharge_area = int(data['AOERechargeArea'])
        except: self.aoe_recharge_area = 0
        try:
            self.aoe_recharge_propability = float(data['AOERechargePropability'])
            if self.aoe_recharge_propability > 1: self.aoe_recharge_propability = 1
            if self.aoe_recharge_propability < 0: self.aoe_recharge_propability = 0
        except: self.aoe_recharge_propability = 0
        try: self.aoe_recharge_type = data['AOERechargeType']
        except: self.aoe_recharge_type = 'fire'

        try: self.start_of_turn_heal = int(data['StartOfTurnHeal'])
        except: self.start_of_turn_heal = 0  #heals this amount at start of turn

        try: self.legendary_resistances = int(data['LegendaryResistances'])
        except: self.legendary_resistances = 0
        self.legendary_resistances_counter = self.legendary_resistances

    #Wild Shape / New Shapes
        self.shape_name = ''
        self.shape_remark = ''
        self.is_shape_changed = False
        self.is_in_wild_shape = False

        self.BeastForms = {
            0:{'Name': 'Wolf', 'Level': 0.25},
            1:{'Name': 'Brown Bear', 'Level': 1},
            2:{'Name': 'Crocodile', 'Level': 0.5},
            3:{'Name': 'Ape', 'Level': 0.5},
            4:{'Name': 'Giant Eagle', 'Level': 1},
            5:{'Name': 'Giant Boar', 'Level': 2},
            6:{'Name': 'Polar Bear', 'Level': 2},
            7:{'Name': 'Boar', 'Level': 0.25}
        }
        self.DruidCR = 0
        self.knows_wild_shape = False
        if 'WildShape' in self.other_abilities:
            self.knows_wild_shape = True
            self.DruidCR = float(data['DruidCR']) #This is the max CR in which the druid can wild shape
            if self.DruidCR < 0.25: self.DruidCR = 0.25 #min CR

        self.knows_combat_wild_shape = False
        if 'CombatWildShape' in self.other_abilities:
            self.knows_combat_wild_shape = True
        self.shape_HP = 0                       #temp HP of the current (different) shape
        self.wild_shape_uses = 2

    #Fight Counter
        self.state = 1                       # 1 - alive, 0 - uncouncious, -1 dead
        self.death_counter = 0
        self.heal_counter = 0
        self.CHP = self.HP                                 #CHP - current HP
        self.THP = 0         #Temporary HitPoints (dont stack)
        self.initiative = 0
        self.attack_counter = self.attacks           #will be reset to attack at start of turn
        self.is_attacking = False #Is set true if player has used acktion to attack
        self.unconscious_counter = 0       #This counts how often the player was unconscious in the fight for the statistics

        self.action = 1
        self.bonus_action = 1
        self.reaction = 1
        self.has_cast_left = True #if a spell is cast, hast_cast_left = False
        self.is_concentrating = False

        #Conditions
        self.restrained = False            #will be ckeckt wenn attack/ed, !!!!!!!!! only handle via Tokens
        self.prone = 0
        self.is_blinded = False    #tokensubtype bl
        self.is_dodged = False    #is handled by the DodgedToken
        self.is_stunned = False   #tokensubtype st
        self.is_incapacitated = False  #tokensubtype ic
        self.is_paralyzed = False  #tokensubtype pl
        self.is_poisoned = False   #tokensubtype ps
        self.is_invisible = False   #tokensubtype iv

        self.last_attacker = 0
        self.dmg_dealed = 0
        self.heal_given = 0

        self.dash_target = False
        self.has_dashed_this_round = False
        self.no_attack_of_opportunity_yet = True

        self.dragons_breath_is_charged = False
        self.spider_web_is_charged = False
        self.recharge_aoe_is_charged = False

    #AI
        self.AI = AI(self)

    def rollD20(self, advantage_disadvantage=0): #-1 is disadvantage +1 is advantage
        d20_1 = int(random()*20 + 1)
        d20_2 = int(random()*20 + 1)
        if advantage_disadvantage > 0:
            d20 = max([d20_1, d20_2])
        elif advantage_disadvantage < 0:
            d20 = min([d20_1, d20_2])
        else:
            d20 = d20_1
        
        #Inspiration hits here, at the top most layer of this simulation, creazy isnt it 
        if self.inspired != 0:
            #Only use it if roll is low, but not that low
            if d20 < 13 and d20 > 6:
                d20 += self.inspired
                self.inspired = 0
                self.is_combat_inspired = False
                self.DM.say('(with inspiration), ')
        return d20

#---------------------Character State Handling----------------
    def unconscious(self):
        self.DM.say(self.name + ' is unconscious ', True)
        self.CHP = 0
        self.state = 0   # now unconscious
        self.unconscious_counter += 1 #for statistics

        #if u get uncounscious:
        self.end_rage()
        self.break_concentration()
        self.TM.unconscious()

        if self.team == 1: #this is for Monsters
            self.state = -1
    
    def get_conscious(self):
        self.DM.say(self.name + ' regains consciousness', True)
        self.state = 1
        self.heal_counter = 0
        self.death_counter = 0

    def death(self):
        self.CHP = 0
        self.state = -1
        #if u die:
        self.end_rage()
        self.break_concentration()
        self.TM.death()

    def check_uncanny_dodge(self, dmg):
        #-----------Uncanny Dodge
        if self.knows_uncanny_dodge:
            if dmg.abs_amount() > 0 and self.reaction == 1 and self.state == 1: #uncanny dodge condition
                dmg.multiply(1/2) #Uncanny Dodge halfs all dmg
                self.reaction = 0
                self.DM.say(' Uncanny Dodge')

    def check_new_state(self, was_ranged):
        #State Handling after Changing CHP

        #----------State Handling Unconscious
        if self.state == 0:         #if the player is dying
            if self.CHP > 0:           #was healed over 0
                self.get_conscious()
            if self.CHP <0:
                if self.CHP < -1*self.HP:
                    self.death()
                    self.DM.say(str(self.name) + ' died due to the damage ', True)
                else:
                    self.CHP = 0
                    if was_ranged:
                        self.death_counter += 1
                    else: #melee is auto crit
                        self.death_counter += 2
                    if self.death_counter >= 3:
                        self.death()
                        self.DM.say(str(self.name) + ' was attacked and died', True)
                    else:
                        self.DM.say(str(self.name) + ' death saves at ' + self.StringDeathCounter(), True)

        #----------State handling alive
        if self.state == 1:                    #the following is if the player was alive before
            if self.CHP < 0-self.HP:              #if more then -HP dmg, character dies
                self.death()
                self.DM.say(str(self.name) + ' died due to the damage ', True)
            if self.CHP <= 0 and self.state != -1:   #if below 0 and not dead, state dying 
                self.unconscious()

    def changeCHP(self, Dmg, attacker, was_ranged):
        self.check_uncanny_dodge(Dmg)

        damage = Dmg.calculate_for(self) #call dmg class, does the Resistances 
        #This calculates the total dmg with respect to resistances

        #-----------Statistics
        if damage > 0:
            attacker.dmg_dealed += damage
            if attacker.is_summoned:   #Append the dmg of summons to summoner
                attacker.summoner.dmg_dealed += damage
            attacker.last_used_DMG_Type = Dmg.damage_type()
        elif damage < 0:
            attacker.heal_given -= damage

        #---------Damage Deal
        AgathysDmg = dmg() #0 dmg
        if damage > 0:                 #if damage, it will be checkt if wild shape HP are still there
            if self.is_a_turned_undead:
                self.end_turned_undead()
            self.make_concentration_check(damage) #Make Concentration Check for the dmg
            #Concentration Checks are done in and outside of wild shape/other shapes
            if self.is_shape_changed:
                self.change_shape_HP(damage, attacker, was_ranged)
                #Not checking resistances anymore, already done 
            else:
                if self.THP > 0:     #Temporary Hitpoints
                    AgathysDmg = self.check_for_armor_of_agathys() #returns the agathys dmg
                    if damage < self.THP: #Still THP
                        self.THP -= damage
                        self.DM.say(self.name + ' takes DMG: ' + Dmg.text() + 'now: ' + str(round(self.CHP,2)) + ' + ' + str(round(self.THP,2)) + ' temporary HP', True)
                        damage = 0
                    else: #THP gone
                        damage = damage - self.THP #substract THP
                        self.THP = 0
                        self.DM.say('temporaray HP empty, ')

                #Change CHP
                if damage > 0: #If still damage left
                    self.CHP -= damage
                    self.DM.say(self.name + ' takes DMG: ' + Dmg.text() + 'now at: ' + str(round(self.CHP,2)), True)

        #---------Armor of Agathys 
        if AgathysDmg.abs_amount() > 0 and was_ranged == False:
            self.DM.say(attacker.name + ' is harmed by the Armor of Agathys', True)
            attacker.changeCHP(AgathysDmg, self, was_ranged=False)

        #---------Heal
        if damage < 0:               #neg. damage is heal Currently Heal is always applied to CHP never to shape HP
            if self.state == -1:
                print('This is stupid, dead cant be healed', True)
                quit()
            if self.chill_touched: 
                self.DM.say(self.name + ' is chill touched and cant be healed.')
            elif abs(self.HP - self.CHP) >= abs(damage):
                self.CHP -= damage    
                self.DM.say(str(self.name) + ' is healed for: ' + str(-damage) + ' now at: ' + str(round(self.CHP,2)), True)
            else:                     #if more heal then HP, only fill HP up
                damage = -1*(self.HP - self.CHP)
                self.CHP -= damage
                self.DM.say(str(self.name) + ' is healed for: ' + str(-damage) + ' now at: ' + str(round(self.CHP,2)), True)

        self.check_new_state(was_ranged)

    def change_shape_HP(self, damage, attacker, was_ranged):
        if damage < self.shape_HP:     #damage hits the wild shape
            self.shape_HP -= damage
            self.DM.say(str(self.name) + ' takes damage in ' + self.shape_remark + ' shape: ' + str(round(damage,2)) + ' now: ' + str(round(self.shape_HP,2)), True)
        else:                  #wild shape breakes, overhang goes to changeCHP
            overhang_damage = abs(self.shape_HP - damage)
            #reshape after critical damage
            self.DM.say(str(self.name) + ' ' + self.shape_remark + ' shape breaks ', True)
            self.drop_shape()  #function that resets the players stats
            #Remember, this function is called in ChangeCHP, so resistances and stuff has already been handled
            #For this reason a 'true' dmg type is passed here
            Dmg = dmg(overhang_damage, 'true')
            self.changeCHP(Dmg, attacker, was_ranged)

    def addTHP(self, newTHP):
        if self.THP == 0: #currently no THP
            self.THP = newTHP
        elif self.has_armor_of_agathys:
            self.THP = newTHP
            self.break_armor_of_agathys()
            #New THP will break the Armor
        else:
            self.THP = newTHP
        self.DM.say(self.name + ' gains ' + str(newTHP) + ' temporary HP', True)

    def stand_up(self):
        rules = [self.prone == 1, self.restrained == 0]
        errors = [self.name + ' tried to stand up but is not prone', 
                self.name + ' tried to stand up, but is restrained']
        ifstatements(rules, errors, self.DM).check()
        self.prone = 0
        self.DM.say(self.name + ' stood up to end prone', True)

    def dps(self):
        #DPS is a reference used to determine the performance of the player so far in the fight
        #It is used by some AI functions to determine the value of the target in a fight
        #This Function returns a value for the dps
        #Heal is values 2 times dmg
        return (self.dmg_dealed + self.heal_given*2)/self.DM.rounds_number

    def value(self):
        #This function is designed to help decision making in AI
        #It returns a current, roughly dmg equal score of the entity to compare how important it is for the team
        #Score that should be roughly a dmg per round equal value
        Score = self.dps() #see .dps() func, is dmg and heal*2 per turn
        if self.is_invisible:
            Score = Score*1.2
        if self.is_hasted:
            Score = Score*1.1

        if self.prone == 1:
            Score = Score*0.95
        if self.restrained == 1:
            Score = Score*0.9
        if self.is_blinded:
            Score = Score*0.9
        if self.is_poisoned:
            Score = Score*0.95
        if self.is_incapacitated:
            Score = Score*0.2
        if self.is_stunned:
            Score = Score*0.15
        if self.is_paralyzed:
            Score = Score*0.1
        return Score

    def update_additional_resistances(self):
        #If this function is called it checks all possible things that could add a resisantace
        self.additional_resistances = ''
        if self.raged == 1:
            self.additional_resistances += 'piercing, bludgeoning, slashing, '
            if self.knows_bear_totem:
                self.additional_resistances += 'acid, cold, fire, force, lightning, thunder, necrotic, poison, radiant'

#---------------------Checks and Saves
    def make_check(self, which_check):  #0-Str, 1-Dex, ...
        d20_roll = self.rollD20()
        result = d20_roll + self.modifier[which_check]  #calc modifier
        return result

    def check_advantage(self, which_save, extraAdvantage = 0, notSilent = True):
        saves_adv_dis = [0,0,0,0,0,0] #calculate all factors to saves:
        text = '' #collect text to say
        if self.restrained == 1:  #disadvantage in dex if restrained
            saves_adv_dis[1] -= 1
            text += 'restrained, '
        if self.is_dodged:
            saves_adv_dis[1] += 1  #dodge adv on dex save
            text += 'dodged, '

        if self.raged == 1:   #str ad if raged
            saves_adv_dis[0] += 1
            text += 'raging, '
        if self.is_hasted:
            saves_adv_dis[1] += 1
            text += 'hasted, '
        if self.is_hexed:
            HexType = int(random()*2 + 1) #random hex disad at Str, Dex or Con
            HexText = ['Str ', 'Dex ', 'Con ']
            text += 'hexed ' + HexText[HexType] + ', '
            saves_adv_dis[HexType] -= 1 #one rand disad 
        if extraAdvantage != 0: #an extra, external source of advantage
            if extraAdvantage > 0:
                text += 'adv, '
            else:
                text += 'disad, '
    
        if notSilent: self.DM.say(text) #only if not silent
        return saves_adv_dis[which_save] + extraAdvantage

    def make_save(self, which_save, extraAdvantage = 0, DC = False):          #0-Str, 1-Dex, 2-Con, 3-Int, 4-Wis, 5-Cha
    #how to disadvantage and advantage here !!!
        save_text = ['Str', 'Dex', 'Con', 'Int', 'Wis', 'Cha']
        self.DM.say(str(self.name) + ' is ', True)
        Advantage = self.check_advantage(which_save, extraAdvantage = extraAdvantage)
        AuraBonus = self.protection_aura()
        if AuraBonus > 0:
            self.DM.say('in protection aura, ')
        if Advantage < 0:
            d20_roll = self.rollD20(advantage_disadvantage=-1)
            self.DM.say('in disadvantage doing a ' + save_text[which_save] + ' save: ')
        elif Advantage > 0:
            d20_roll = self.rollD20(advantage_disadvantage=1)
            self.DM.say('in advantage doing a ' + save_text[which_save] + ' save: ')
        else:
            d20_roll = self.rollD20(advantage_disadvantage=0)
            self.DM.say('doing a ' + save_text[which_save] + ' save: ')

        modifier = self.modifier[which_save]
        if save_text[which_save] in self.saves_prof: #Save Proficiency
            modifier += self.proficiency
        result = d20_roll + modifier + AuraBonus #calc modifier

        #Legendary Resistances
        if result < DC and self.legendary_resistances_counter > 0:
            self.legendary_resistances_counter -= 1
            self.DM.say(self.name + ' uses a legendary resistance: ' + str(self.legendary_resistances_counter) + '/' + str(self.legendary_resistances))
            return 10000  #make sure to pass save
        else:
            #Just display text 
            roll_text = str(int(d20_roll)) + ' + ' + str(int(modifier))
            if AuraBonus != 0: roll_text += ' + ' + str(int(AuraBonus))
            if DC != False: roll_text += ' / ' + str(DC) + ' '
            self.DM.say(roll_text)
            return result

    def make_death_save(self):
        d20_roll = int(random()*20 + 1)
        AuraBonus = self.protection_aura()
        if AuraBonus > 0:
            d20_roll += AuraBonus
            self.DM.say(''.join(['Aura of protection +',str(int(AuraBonus)),' : ']), True)
        self.DM.say(self.StringDeathCheck(d20_roll), True)
        if self.death_counter >= 3:
            self.death()
            self.DM.say(str(self.name) + ' failed death save and died', True)
        if self.heal_counter >= 3:
            self.CHP = 1
            self.get_conscious()

    def StringDeathCheck(self, d20_roll):
        if d20_roll < 11:
            self.death_counter += 1
            TextResult = str(self.name) + ' did not made the death save '
        elif d20_roll > 10 and d20_roll != 20:
            self.heal_counter += 1
            TextResult = str(self.name) + ' made the death save'
        if d20_roll == 20:
            self.heal_counter += 2
            TextResult = str(self.name) + ' made the death save critical'
        TextResult += self.StringDeathCounter()
        return TextResult

    def StringDeathCounter(self):
        text = '(' + str(self.death_counter) + '-/' + str(self.heal_counter) + '+)'
        return text 

#---------------Concentration and Conjuration Spells-----------
    def make_concentration_check(self, damage):
        if self.is_concentrating:
            saveDC = 10
            if damage/2 > 10: saveDC = int(damage/2)
            save_res = self.make_save(2, DC=saveDC)
            if save_res >= saveDC:   #concentration is con save
                return 
            else:
                self.break_concentration()
                return 
        else:
            return

    def break_concentration(self):
        self.TM.break_concentration()
        #Will test for concentration tokens
        #If Concentration breaks, it will say so

    def break_armor_of_agathys(self):
        if self.has_armor_of_agathys and self.THP > 0:
            self.has_armor_of_agathys = False
            self.THP = 0
            self.agathys_dmg = 0
            self.DM.say(self.name + ' Armor of Agathys breaks, ')
        else:
            print(self.name + ' Armor of Agathys broke without having one')
            quit()

    def break_spiritual_weapon(self):
        if self.has_spiritual_weapon:
            self.has_spiritual_weapon = False
            self.SpiritualWeaponCounter = 0 #reset counter
            self.SpiritualWeaponDmg = 0
            self.DM.say('Spiritual Weapon of ' + self.name + ' vanishes, ')
    
    def end_turned_undead(self):
        self.is_a_turned_undead == False #no longer turned
        self.turned_undead_round_counter = 0
        self.DM.say(self.name + ' is no longer turned', True)

#--------------------Position Management----------------------
    def need_dash(self, target, fight, AttackIsRanged = False):
        #0 - need no dash
        #1 - need dash
        #2 - not reachable

        #ABack-25ft-AMid-25ft-AFront-BFront-25ft-BMid-25ft-BBack
        #no Dash for ranged attacks
        if AttackIsRanged: return 0 
        if self.has_range_attack: return 0
        if target.position == 3: return 0 #Airborn is in range

        #The Distance between lines scales with how dense the Battlefield is
        # 0 Wide Space
        # 1 normal
        # 2 crowded
        distance = 25
        if self.DM.density == 0:
            distance = 50
        elif self.DM.density == 2:
            distance = 12.5


        EnemiesLeft = [x for x in fight if x.team != self.team and x.state == 1]
        EnemiesInFront = [Enemy for Enemy in EnemiesLeft if Enemy.position == 0]
        EnemiesInMid = [Enemy for Enemy in EnemiesLeft if Enemy.position == 1]

        if self.position < 3: #0,1,2 Front, Mid, Back
            if len(EnemiesInFront) == 0 and len(EnemiesInMid) == 0: OpenLines=2 #open Front and Mid
            elif len(EnemiesInFront) == 0: OpenLines = 1 #open front
            else: OpenLines = 0 #no open line
        if self.position == 3: #airborn
            if target.position < 3: OpenLines=3 #basically 3 open lines
            else: return 0

        #Test if Dash is ness        
        #example: Mid Attacks Mid, no open front: 1 + 1 = 2*25ft = 50ft 
        if self.speed >= (target.position + self.position - OpenLines)*distance: return 0
        elif self.dash_target == target: return 0 #The player has used dash last round to get to this target
        #Only works if you can still dash with action or cunning action or eagle totem
        elif self.action == 1 or (self.knows_cunning_action and self.bonus_action ==1) or (self.knows_eagle_totem and self.bonus_action ==1):
            if 2*self.speed >= (target.position + self.position - OpenLines)*distance: return 1
            else: return 2 
        else: return 2

    def will_provoke_Attack(self, target, fight, AttackIsRanged = False):
        #this function tells if an attack of opportunity will be provoked
        if AttackIsRanged: return False
        if self.has_range_attack: return False
        if self.dash_target == target: return False

        EnemiesLeft = [x for x in fight if x.team != self.team and x.state == 1]
        EnemiesInFront = [Enemy for Enemy in EnemiesLeft if Enemy.position == 0]
        EnemiesInMid = [Enemy for Enemy in EnemiesLeft if Enemy.position == 1]
        
        #Open Lines
        if self.position < 3: #0,1,2 Front, Mid, Back
            if len(EnemiesInFront) == 0 and len(EnemiesInMid) == 0: return False #open Front and Mid
            elif len(EnemiesInFront) == 0: OpenLines = 1 #open front
            else: OpenLines = 0 #no open line
        if self.position == 3: return False #no opp. attacks from the air

        #Compare Lines
        #if you cross more then 2 lines (like, front - back or mid - mid) you provoke opp. attack
        if self.position == 2:
            OpenLines += 1 #back Player can attack Front with no Opp Attack 
        if self.position + target.position - OpenLines >= 2:
            return True 
        else: return False

    def use_disengage(self):
        if self.bonus_action == 1 and self.knows_cunning_action:
            self.DM.say(self.name + ' used cunning action to disengage', True)
            self.bonus_action = 0
        elif self.action == 1:
            self.DM.say(self.name + ' used an action to disengage', True)
            self.action = 0
        else:
            print(self.name + ' tried to disengage, but has no action left', True)
            quit()

    def enemies_reachable_sort(self,fight, AttackIsRanged = False):
        #This function is used to determine which Enemies are theoretically in reach to attack for a Player
        #This also includes Players, that are only reachable by dashing or by provoking attacks of Opportunity

        #The following Rules Apply
        #----------0---------
        #Front can always melee attack the other front
        #Front can attack the other mid, if the player speed suffice
        #Front can attack the other back, if player speed suffice and by provoking an opportunity attack
        #If there is no Player in the other Front, the Front can melee attack mid and back
        #If there is no front, the distance to mid and back reduces
        #----------1---------
        #mid can meelee attack front
        #mid can attack mid, if speed suffices, and by provoking an opportunity attack
        #If there is no Player in the other Front, the mid can melee attack mid and back
        #If there is no Player in the other Front and Mid, mid can attack all
        #----------2---------
        #back can attack Front
        #----------3---------
        #airborn can melee attack all, but must land for that
        #if airborn lands, it is then in front
        #Airborn can not be attacked by melee at this point
        #----------R---------
        #If player has reanged attacks, player can attack all regardless

        #Idea: Line Airborn, only hittable by ranged 
        #At the start of turn, a creature desides to go airborn or land

        #This includes Character Players that are unconscious        
        EnemiesNotDead = [x for x in fight if x.team != self.team and (x.state == 1 or (x.team != 1 and x.state == 0))]
        
        if AttackIsRanged: return EnemiesNotDead #Everyone in Range
        if self.has_range_attack: return EnemiesNotDead #Everyone in Range
        if self.position == 3: return EnemiesNotDead #Everyone in Range
        
        EnemiesInFront = [Enemy for Enemy in EnemiesNotDead if Enemy.position == 0]
        EnemiesInMid = [Enemy for Enemy in EnemiesNotDead if Enemy.position == 1]
        

        EnemiesInReach = []

        for i in range(0,len(EnemiesNotDead)):
        #This is to manually tell the function that the Attack is ranged, even if the player might not have ranged attacks, for Spells for example
            Enemy = EnemiesNotDead[i]
            if Enemy == self.dash_target: #last dash target is always in reach
                EnemiesInReach.append(Enemy) #Is in range 
                continue

        #All other lines front(0), mid(1), back(2)
            if self.position == 1:
                if Enemy.position == 2 and len(EnemiesInFront) != 0:
                    continue
            if self.position == 2:
                if Enemy.position == 1 and len(EnemiesInFront) != 0:
                    continue
                if Enemy.position == 2 and len(EnemiesInFront) != 0:
                    continue
                if Enemy.position == 2 and len(EnemiesInMid) != 0:
                    continue
            if Enemy.position == 3 and self.position !=3:
                continue
            DashValue = self.need_dash(Enemy, fight, AttackIsRanged= False)
            if DashValue == 2: #target is too far away
                continue
            
            #No False case, so in range
            EnemiesInReach.append(Enemy)
        return EnemiesInReach

    def use_dash(self, target):
        if self.knows_cunning_action and self.bonus_action == 1:
            self.DM.say(self.name + ' uses cunning action to dash to ' + target.name, True)
            is_BADash = True 
        elif self.knows_eagle_totem and self.bonus_action == 1:
            self.DM.say(self.name + ' uses eagle totem to dash to ' + target.name, True)
            is_BADash = True
        else:
            is_BADash = False
        if is_BADash:
            self.bonus_action = 0
            self.dash_target = target
            self.has_dashed_this_round = True
        elif self.action == 1:
            self.action = 0
            self.attack_counter = 0
            self.dash_target = target
            self.has_dashed_this_round = True
            self.DM.say(self.name + ' uses dash to get to ' + target.name, True)
        else:
            print(self.name + ' tried to dash, but has no action left', True)
            quit()

    def move_position(self):
        #This function will be called, if the player hat no target in reach last turn
        if self.position == 1: #if you are usually in mid go front 
            self.DM.say(self.name + ' moves to the front line', True)
            self.position = 0
            self.action = 0 #took the action

    def use_dodge(self):
        if self.action == 0:
            print(self.name + ' tried to dodge without action')
            quit()
        self.DM.say(self.name + ' uses its turn to dodge', True)
        self.action = 0 #uses an action to do
        DodgeToken(self.TM) #give self a dodge token
        #The dodge token sets and resolves self.is_dodge = True

#-------------------Attack Handling----------------------
    def make_attack_check(self, target, fight, is_off_hand):
        if self.action == 0 and self.is_attacking == False and is_off_hand == False:
            print(self.name + ' tried to attack, but has no action left')
            quit()
        elif self.bonus_action == 0 and is_off_hand:
            print(self.name + ' tried to offhand attack, but has no bonus attacks left')
            quit()
        elif is_off_hand and self.is_attacking == False:
            print(self.name + ' tried to offhand attack, but has not attacked with action')
            quit()
        elif self.attack_counter < 1 and is_off_hand == False:
            print(self.name + ' tried to attack, but has no attacks left')
            quit()
        elif self.state != 1:
            print(self.name +' treid to attack but is not conscious')
            quit()
        #check if target is in range
        elif target not in self.enemies_reachable_sort(fight):
            print(self.name + ' tried to attack, but ' + target.name + ' is out of reach')
            quit()            

    def check_dash_and_op_attack(self, target, fight, NeedDash):
        if NeedDash == 1:
            self.use_dash(target)
        if self.will_provoke_Attack(target, fight):
            if self.no_attack_of_opportunity_yet:#only one per turn
                #now choose whos doing the attack of opportunity
                EnemiesLeft = [x for x in fight if x.team != self.team and x.state == 1]
                EnemiesInFront = [Enemy for Enemy in EnemiesLeft if Enemy.position == 0]
                if len(EnemiesInFront) > 0:
                    OpportunityAttacker = EnemiesInFront[int(random()*len(EnemiesInFront))]
                else:
                    OpportunityAttacker = EnemiesLeft[int(random()*len(EnemiesLeft))]
                if self.provoke_opportunit_attack(OpportunityAttacker) == False:
                    #false means that the attack killed the player
                    return #return and end the turn

    def make_normal_attack_on(self, target, fight, is_off_hand=False):
    #This is the function of a player trying to move to a target und making an attack
    #It also checks for Dash and does opportunity attacks if necessary

    #First Check for attck_counter
        self.make_attack_check(target, fight, is_off_hand)
        #target is within reach
        NeedDash = self.need_dash(target, fight)
        if NeedDash == 2:
            print(self.name + ' tried to attack, but ' + target.name + ' is out of reach, this is weird here, check enemies_rechable_sort')
            quit()
        #----attack of opportunity and dash
        self.check_dash_and_op_attack(target, fight, NeedDash)

        #The Player is now in range for attack
        is_ranged = False
        if self.has_range_attack: is_ranged = True

        if self.attack_counter == 0 and is_off_hand == False:
            #If you used the action to dash, return and end your turn here, if cunning action, then proceed
            return
        if is_off_hand:
            #Make Offhand Attack
            self.bonus_action = 0
            self.attack(target, is_ranged, other_dmg=self.offhand_dmg, is_offhand=True, is_spell=False)
        else:
            self.check_polearm_master(target, is_ranged) #Check if target is a polearm master
            self.action = 0 #if at least one attack, action = 0
            self.is_attacking = True #uses action to attack
            self.attack_counter -= 1 #Lower the attack counter 
            self.attack(target, is_ranged)

    def provoke_opportunit_attack(self, target):
        if self.no_attack_of_opportunity_yet: #only one per turn 
            self.DM.say(self.name + ' has provoked an attack of opportunity:', True)
            self.no_attack_of_opportunity_yet = False
            target.AI.do_opportunity_attack(self)
            if self.state != 1: return False
            else: return True
        else: return True

    def check_attack_advantage(self, target, is_ranged, is_opportunity_attack):
        #This function returns if an attack is advantage or disadvantage
        #No stats or tokens should be changed here, it is just a check
        #calculate all effects that might influence Disad or Advantage
        advantage_disadvantage = 0
        if target.state == 0:
            advantage_disadvantage += 1 #advantage against unconscious
            self.DM.say(target.name + ' unconscious, ')

        if target.reckless == 1:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' reckless, ')
        if self.reckless == 1:
            advantage_disadvantage += 1    
            self.DM.say(self.name + ' reckless, ')
        if target.knows_eagle_totem and is_opportunity_attack:
            advantage_disadvantage -= 1
            #disadvantage for opp. att against eagle totem
            self.DM.say('eagle totem, ')
        if self.knows_assassinate:
            if self.DM.rounds_number == 1 and self.initiative > target.initiative:
                #Assassins have advantage against player that have not had a turn
                advantage_disadvantage += 1
                self.DM.say(self.name + ' assassinte, ')
        if target.has_wolf_mark and is_ranged == False:
            self.DM.say(target.name + ' has wolf totem, ')
            advantage_disadvantage += 1

        #Conditions
        if target.restrained == 1:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' restrained, ')
        if self.restrained == 1:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' restrained, ')
        if target.is_dodged:
            advantage_disadvantage -= 1
            self.DM.say(target.name + ' dodged, ',)
        if target.is_blinded:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' blinded, ')
        if self.is_blinded:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' blinded, ')
        if target.is_stunned:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' stunned, ')
        if self.is_invisible:
            advantage_disadvantage += 1
            self.DM.say(self.name + ' invisible')
        if target.is_invisible:
            advantage_disadvantage -= 1
            self.DM.say(target.name + ' invisible')
        if target.is_paralyzed:
            advantage_disadvantage += 1
            self.DM.say(target.name + ' paralyzed')
        if self.is_poisoned:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' poisoned')

        if target.prone == 1:
            if is_ranged:
                advantage_disadvantage -=1 #disad for ranged against prone
            else:
                advantage_disadvantage += 1
            self.DM.say(target.name + ' prone, ')
        if self.prone == 1:
            advantage_disadvantage -= 1
            self.DM.say(self.name + ' prone, ')
        if target.is_guiding_bolted:
            #This is set by the guidingBolted Token triggered bevore
            self.DM.say('guiding bolt, ')
            advantage_disadvantage += 1
            #Being guiding boltet is reset at the make_attack_roll function
            #It should not happen here, as I want to use this function also for AI stuff
            #It should therefor not change any status
        return advantage_disadvantage

    def make_attack_roll(self, target, is_ranged, is_opportunity_attack):
        #calculate all effects that might influence Disad or Advantage
        advantage_disadvantage = self.check_attack_advantage(target, is_ranged, is_opportunity_attack)
        if target.is_guiding_bolted:
            target.is_guiding_bolted = False #reset being boltet
            
        #Roll the Die to hit
        if advantage_disadvantage > 0:
            d20 = self.rollD20(advantage_disadvantage=1)
            self.DM.say('Advantage: ')
        elif advantage_disadvantage < 0:
            d20 = self.rollD20(advantage_disadvantage=-1)
            self.DM.say('Disadvantage: ')
        else:
            d20 = self.rollD20(advantage_disadvantage=0)
        #The roll and advantage is returned, advantage is still important for sneak attack
        return d20 , advantage_disadvantage

    def check_polearm_master(self, target, is_ranged):
        #This function is called in the make normal attack function
        #At this point it is already clear it is no offhand attack and no opp. attack
        if target.knows_polearm_master:
            rules = [is_ranged == False,  #No range attacks
                     target.last_attacker != self, #if attacked before, you didnt just enter their range
                     target.reaction == 1]  #has reaction left
            if all(rules):
                self.DM.say(self.name + ' has entered the polearm range of ' + target.name, True)
                target.AI.do_opportunity_attack(self)

    def check_smite(self, target, Dmg, is_ranged, is_spell):
        if is_ranged == False and self.knows_smite and is_spell == False:  #smite only on melee
            slot = self.AI.want_to_use_smite(target) #returns slot or false
            if slot != False and self.spell_slot_counter[slot-1] > 0:
                #DMG calc
                if slot > 4: smitedmg = 4.5*5 #5d8 max
                else: smitedmg = 4.5*(slot + 1) #lv1 -> 2d8
                if target.type in ['undead', 'fiend']: smitedmg += 4.5 #extra d8 

                Dmg.add(smitedmg, 'radiant')
                self.spell_slot_counter[slot - 1] -= 1
                self.DM.say(''.join([self.name,' uses ',str(slot),'. lv Smite: +',str(smitedmg)]), True)

    def check_sneak_attack(self, Dmg, advantage_disadvantage, is_spell):
        if self.sneak_attack_dmg > 0:    #Sneak Attack 
            rules = [self.sneak_attack_counter == 1, 
                     advantage_disadvantage >= 0, #not in disadv.
                     is_spell == False
                     ]
            if all(rules):
                Dmg.add(self.sneak_attack_dmg, self.damage_type)
                self.DM.say(''.join([self.name,' Sneak Attack: +', str(self.sneak_attack_dmg)]), True)
                if self.wailsfromthegrave == 1 and self.wailsfromthegrave_counter > 0:  #if sneak attack hits and wails from the grave is active
                    Dmg.add(self.sneak_attack_dmg/2, 'necrotic')
                    self.wailsfromthegrave_counter -= 1
                    self.DM.say(' and ' + str(self.sneak_attack_dmg/2) + ' wails from the grave')
                self.sneak_attack_counter = 0

    def check_combat_inspiration(self, Dmg, is_spell):
        if self.is_combat_inspired and self.inspired > 0 and is_spell == False:
            #Works only for weapon dmg, so other_dmg == False
            Dmg.add(self.inspired, self.damage_type)
            self.DM.say(self.name + ' uses combat inspiration: +' + str(self.inspired), True)
            self.inspired = 0
            self.is_combat_inspired = False

    def check_great_weapon_fighting(self, Dmg, is_ranged, other_dmg, is_spell):
        rules = [self.knows_great_weapon_fighting,
                self.offhand_dmg == 0,  #no offhand
                is_ranged == False,     #no range
                is_spell == False]   #no spells or stuff
        if all(rules):
            self.DM.say(self.name + ' uses great weapon fighting', True)
            Dmg.multiply(1.15) #no 1,2 in dmg roll, better dmg on attack

    def pre_hit_modifier(self, target, Dmg, d20, advantage_disadvantage, is_crit, is_spell, is_ranged, is_offhand):
        #Does the target AI wants to use Reaction to cast shield? 
        if target.state == 1: #is still alive?
            if target.reaction == 1 and 'Shield' in target.SpellBook:
                target.AI.want_to_cast_shield(self, Dmg)  #call the target AI for shield

        Modifier = 0 # Will go add to the attack to hit
        ACBonus = 0
        AdditionalDmg = 0 #This is damage that will not be multiplied

        if self.knows_great_weapon_master:
            rules = [is_spell == False, #No spells or other stuff
                        is_ranged == False, is_offhand == False]
            if all(rules): #No spells or range attacks
                #Do you want to use great_weapon_master
                if self.AI.want_to_use_great_weapon_master(target, advantage_disadvantage):
                    Modifier -=5  #-5 to attack but +10 to dmg
                    AdditionalDmg += 10
                    self.DM.say('great weapon master, ')
                
                if is_crit and self.bonus_action == 1: 
                    #Just made a crit meele attack, take BA for another attack
                    self.DM.say('extra attack through crit, ')
                    self.bonus_action = 0
                    self.attack_counter += 1
                
                #Inititate Token
                #This Token resolves at end of turn
                #If target gets unconcious in this turn, the Token triggers and gives another attack to player
                GreatWeaponToken(self.TM, GreatWeaponAttackToken(target.TM, subtype='gwa'))

        if target.is_combat_inspired and target.inspired > 0:
            if d20 + self.tohit > target.AC:
                self.DM.say('combat inspired AC (' + str(target.inspired) + '), ')
                ACBonus += target.inspired
                target.inspired = 0
                target.is_combat_inspired = False

        #Gives Bard Chance to protect himself with cutting Words
        if target.knows_cutting_words and target.inspiration_counter > 0:
            if d20 + self.tohit > target.AC:
                self.DM.say(target.name + ' uses cutting word, ')
                Modifier += -target.inspiration_die
                target.inspiration_counter -= 1 #One Use
                target.reaction = 0 #uses reaction
        
        if self.knows_archery and is_ranged and is_spell == False:
            self.DM.say(self.name + ' uses Archery, ')
            Modifier += 2 #Archery

        return Modifier, ACBonus, AdditionalDmg

    def attack(self, target, is_ranged, other_dmg = False, damage_type = False, tohit = False, is_opportunity_attack = False, is_offhand = False, is_spell = False):
    #this is the attack funktion of a player attacking a target with a normak attack
    #if another type of dmg is passed, it will be used, otherwise the player.damage_type is used
    #if no dmg is passed, the normal entitiy dmg is used
    #is_ranged tells the function if it is a meely or ranged attack
        #this ensures that for a normal attack the dmg type of the entity is used
        if damage_type == False: damage_type = self.damage_type
        #if no other dmg is passed, use that of the player
        if other_dmg == False: Dmg = dmg(self.dmg, damage_type)
        else: Dmg = dmg(other_dmg, damage_type)

        #check if other to hit is passsed, like for a spell
        if tohit == False: tohit = self.tohit
        target.TM.isAttacked(self, is_ranged, is_spell)     #Triggers All Tokens, that trigger if target is attacked
        if self.state != 1: return 0   #maybe already dead because of attack of opp or token

        self.DM.say(self.name + " -> " + target.name + ', ', True)

        if is_ranged: self.DM.say('ranged, ')
        else: self.DM.say('melee, ')
        if is_offhand: self.DM.say('off hand, ')

        #Advantage still important for sneak attack
        d20, advantage_disadvantage = self.make_attack_roll(target, is_ranged, is_opportunity_attack)
                
        if d20 == 20 or (self.knows_improved_critical and d20 == 19):
            is_crit = True
        else:
            is_crit = False

        Modifier, ACBonus, AdditionalDmg  = self.pre_hit_modifier(target, Dmg, d20, advantage_disadvantage, is_crit, is_spell, is_ranged, is_offhand)

    #-----------------Hit---------------
        if d20 + tohit + Modifier >= target.AC + ACBonus or is_crit:       #Does it hit
            if is_crit:
                self.DM.say('Critical Hit!, ')
            text = ''.join(['hit: ',str(d20),'+',str(tohit),'+',str(Modifier),'/',str(target.AC),'+',str(ACBonus)])
            self.DM.say(text)

        #Smite
            self.check_smite(target, Dmg, is_ranged, is_spell)
        #Snackattack
            self.check_sneak_attack(Dmg, advantage_disadvantage, is_spell)
        #Combat Inspiration 
            self.check_combat_inspiration(Dmg, is_spell)
        #GreatWeaponFighting
            self.check_great_weapon_fighting(Dmg, is_ranged, other_dmg, is_spell)
        #Favored Foe
            if self.knows_favored_foe:
                if self.AI.want_to_use_favored_foe(target) and self.favored_foe_counter > 0 and self.is_concentrating == False:
                    self.use_favored_foe(target)
        #Stunning Strike
            if self.knows_stunning_strike and is_ranged == False:
                if self.ki_points > 0:
                    if target.is_stunned == False: #don't double stunn
                        self.use_stunning_strike(target)
        #Tokens
            target.TM.washitWithAttack(self, Dmg, is_ranged, is_spell) #trigger was hit Tokens
            self.TM.hasHitWithAttack(target, Dmg, is_ranged, is_spell) #trigger was hit Tokens

        #poison Bite
            if self.knows_poison_bite and self.poison_bites == 1 and is_spell == False and is_offhand == False:
                self.poison_bites = 0 #only once per turn
                poisonDMG = self.poison_bite_dmg
                poisonDC = self.poison_bite_dc
                self.DM.say(self.name + ' uses poison bite, ', True)
                if target.make_save(2, DC = poisonDC) >= poisonDC: #Con save
                    poisonDMG = poisonDMG/2
                Dmg.add(poisonDMG, 'poison')
        #Critical
            if is_crit: Dmg.multiply(1.8)
        #Additional damage
            if AdditionalDmg != 0: Dmg.add(AdditionalDmg, self.damage_type)
        #add rage dmg
            if self.raged == True and is_ranged == False: #Rage dmg only on melee
                Dmg.add(self.rage_dmg, self.damage_type)
        #Interception
            if target.interception_amount > 0:
                self.DM.say(' Attack was intercepted: -' + str(target.interception_amount))
                Dmg.substract(target.interception_amount)
                target.interception_amount = 0 #only once
        #Deflect Missile
            if target.knows_deflect_missiles and is_ranged:
                if target.reaction == 1:
                    #ask AI if player wants to reduce dmg with reaction
                    #and if so, if it also wants to return attack if possible
                    wants_to_reduce_dmg, wants_to_return_attack = target.AI.want_to_use_deflect_missiles(self, Dmg)
                    if wants_to_reduce_dmg:
                        target.use_deflect_missiles(self, Dmg, wants_to_return_attack)

        else:
            Dmg = dmg(amount=0)   #0 dmg
            self.DM.say(''.join(['miss: ',str(d20),'+',str(tohit),'+',str(Modifier),'/',str(target.AC),'+',str(ACBonus)]))
        target.changeCHP(Dmg, self, is_ranged)  #actually change HP
        target.last_attacker = self
        if self.knows_wolf_totem:
            target.has_wolf_mark = True #marked with wolf totem
        return Dmg.abs_amount()

#-------------------Shape Changing, Wild Shape--------------
    def assume_new_shape(self, ShapeName, ShapeDict, Remark = ''):
        #Takes a dict as input for the shape properties
        #Shape Properties
        self.is_shape_changed = True
        self.name = self.orignial_name + '(' + ShapeName + ')'
        self.shape_name = ShapeName
        self.shape_remark = Remark
        self.AC = ShapeDict['AC']
        self.shape_AC = ShapeDict['AC']
        self.shape_HP = ShapeDict['HP']
        self.tohit = ShapeDict['To_Hit']
        self.type = ShapeDict['Type']

        #number auf Attacks
        self.attacks = ShapeDict['Attacks']
        self.attack_counter = self.attacks
        self.dmg = ShapeDict['DMG']

        #new Stats/Modifier
        ShapeStatList = [
            ShapeDict['Str'],
            ShapeDict['Dex'],
            ShapeDict['Con'],
            ShapeDict['Int'],
            ShapeDict['Wis'],
            ShapeDict['Cha']
        ]
        ShapeModList = [round((self.stats_list[i] -10)/2 -0.1, 0) for i in range(0,6)]  #calculate the shape mod
        self.stats_list = ShapeStatList
        self.modifier = ShapeModList

        #new dmg types
        self.damage_type = ShapeDict['Damage_Type']
        self.damage_resistances = ShapeDict['Damage_Resistance']
        self.damage_immunity = ShapeDict['Damage_Immunity']
        self.damage_vulnerability = ShapeDict['Damage_Vulnerabilities']

    def drop_shape(self):
        #If Shape Changed, reset all the changed attributes back to base
        if self.is_shape_changed:
            self.name = self.orignial_name
            self.shape_remark = ''
            self.shape_AC = self.base_AC  #set the shape AC of Entity back to base AC (for more see __init__)
            self.AC = self.shape_AC #set current AC back
            self.shape_HP = 0
            self.tohit = self.base_tohit
            self.attacks = self.base_attacks
            self.attack_counter = 0 #is set to zero, so no attacks can occure in new form, until start of new turn, where they will be reset
            self.dmg = self.base_dmg
            self.type = self.base_type
            
            self.modifier = self.base_modifier
            self.stats_list = self.base_stats_list

            self.damage_immunity = self.base_damage_immunity
            self.damage_resistances = self.base_damage_resistamces
            self.damage_vulnerability = self.base_damage_vulnerability
            self.damage_type = self.base_damage_type

            self.is_shape_changed = False  #no longer shape changed
            self.is_in_wild_shape = False  #definately no longer in wild shape
            self.shape_name = ''            
            self.TM.hasDroppedShape() #some Tokens trigger here, like polymorph

    def wild_shape(self, ShapeIndex):
        #ShapeIndex is Index in BeastFroms from entity __init__
        #Wild shape needs an action or a bonus action if you know combat_wild_shape
        rules = [
            self.knows_wild_shape,
            self.wild_shape_uses > 0,
            self.is_shape_changed == False,
            self.DruidCR >= self.BeastForms[ShapeIndex]['Level']
        ]
        errors = [
                self.name + ' tried to go into wild shape without knowing how',
                self.name + ' cant go into wild shape anymore',
                self.name + ' cant go into wild shape while chape changed',
                self.name + ' tried to go into a too high CR shape: ' + str(self.BeastForms[ShapeIndex]['Level'])
        ]
        ifstatements(rules, errors, self.DM)

        if self.bonus_action == 1 and self.knows_combat_wild_shape:
            self.bonus_action = 0
        elif self.action == 1:
            self.action = 0
        else:
            print('no action left for wildshape')
            quit()

        #A Shape form is choosen and then initiated as entity to use their stats
        ShapeName = self.BeastForms[ShapeIndex]['Name']
        NewShape = entity(ShapeName, self.team, self.DM, archive=True)
        #Use Stats to create dict for shape change function
        ShapeDict = {
            'AC' : NewShape.AC, 
            'HP' : NewShape.HP,
            'To_Hit' : NewShape.tohit,
            'Type' : NewShape.type,
            'Attacks' : NewShape.attacks,
            'DMG' : NewShape.dmg,
            'Str' : NewShape.Str,
            'Dex' : NewShape.Dex,
            'Con' : NewShape.Con,
            'Int' : NewShape.Int,
            'Wis' : NewShape.Wis,
            'Cha' : NewShape.Cha,
            'Damage_Type' : NewShape.damage_type,
            'Damage_Resistance' : NewShape.damage_resistances, 
            'Damage_Immunity' : NewShape.damage_immunity,
            'Damage_Vulnerabilities' : NewShape.damage_vulnerability
        }
        self.assume_new_shape(ShapeName, ShapeDict, Remark= 'wild')

        self.is_in_wild_shape = True
        self.DM.say(self.name + ' goes into wild shape ' + ShapeName, True)
        self.wild_shape_uses -= 1

    def wild_reshape(self):
        if self.bonus_action == 1 and self.is_in_wild_shape:
            self.bonus_action = 0
            self.drop_shape() #resets all shape prop. to base
            self.DM.say(self.name + ' drops wild shape', True)
        else:
            if self.is_in_wild_shape == False:
                print(self.name + ' tried to drop wild shape, but is not in wild shape')
                quit()
            else:
                print(self.name + ' tried to drop wild shape, but has no bonus action left')
                quit()

    def use_combat_wild_shape_heal(self, spell_level=1):
        rules = [self.knows_combat_wild_shape,
                self.is_in_wild_shape,
                self.spell_slot_counter[spell_level -1] > 0,
                self.bonus_action == 1]
        errors = [self.name + ' tried to heal by combat wild shape but does not know how',
                self.name + ' tried to heal by combat wild shape but is not in wild shape',
                self.name + ' tried to heal by combat wild shape but has no bonus action left',
                self.name + ' tried to heal by combat wild shape with a ' + str(spell_level) + 'lv spell slot but has non left']
        ifstatements(rules, errors, self.DM).check()

        heal = spell_level*4.5
        self.changeCHP(dmg(-heal, 'heal'), self, was_ranged=False)
        #HEal is currently always applied to CHP not Shape HP 
        self.spell_slot_counter[spell_level -1] -= 1
        self.bonus_action -= 1

#------------------Special Abilities-----------------
    def rackless_attack(self):
        if self.knows_reckless_attack:
            self.reckless = 1
            self.DM.say(self.name + ' uses reckless Attack', True)
        else:
            print(self.name + ' tried to reckless Attack without knowing it')
            quit()

    def rage(self):
        #rage dmg is added in attack function
        if self.bonus_action == 1 and self.knows_rage:
            self.bonus_action = 0
            self.raged = 1
            self.update_additional_resistances()
            rage_text = self.name + ' falls into a'
            if self.knows_bear_totem:
                rage_text += ' bear totem'
            if self.knows_eagle_totem:
                rage_text += ' eagle totem'
            if self.knows_frenzy:
                self.is_in_frenzy = True
                rage_text += ' franzy'
            self.DM.say(rage_text + ' rage', True)
        else:
            if self.bonus_action == 0:
                print(self.name + ' tried to rage, but has no bonus action')
                quit()
            elif self.knows_rage == False:
                print(self.name + ' tried to rage but cant')
                quit()

    def use_frenzy_attack(self):
        if self.is_in_frenzy and self.bonus_action == 1:
            self.DM.say(self.name + ' uses the bonus action for a frenzy attack', True)
            self.attack_counter += 1  #additional attack
            self.bonus_action = 0
        elif self.bonus_action == 0:
            print(self.name + ' tried to use frenzy attack without a bonus action')
            quit()
        elif self.is_in_frenzy == False:
            print(self.name + ' tried to use franzy attack but is not in a frenzy rage')
            quit()

    def end_rage(self):
        if self.raged == 1:
            self.raged = 0
            self.update_additional_resistances()
            self.is_in_frenzy = False
            self.DM.say(self.name + ' falls out of rage, ')

    def inspire(self, target):
        if self.bonus_action == 0:  #needs a bonus action
            print(self.name + ' tried to use bardic inspiration but has no bonus action left')
            quit()
        else:
            if self.inspiration_counter > 0:
                self.bonus_action = 0
                target.inspired = self.inspiration_die
                #Combat Inspiration
                CombatInspirationText = ''
                if self.knows_combat_inspiration:
                    target.is_combat_inspired = True 
                    CombatInspirationText = ' combat'

                self.inspiration_counter -= 1
                self.DM.say(''.join([self.name,CombatInspirationText,' inspired ',str(target.name),' with awesomeness']), True)
            else:
                print(self.name + ' tried to use bardic inspiration but has none left')
                quit()

    def use_lay_on_hands(self, target, heal):
        if self.action == 0:
            print(self.name + ' tried to lay on hands, but has no action left')
            quit()
        elif heal <= 0:
            print('Lay on Hands was called with a negative heal')
            quit()
        elif self.lay_on_hands_counter <= 0:
            print(self.name + ' tried to lay on hands, but has no points left')
            quit()
        else:
            if self.lay_on_hands_counter > heal:
                self.lay_on_hands_counter -= heal
            elif self.lay_on_hands_counter > 0:
                heal = self.lay_on_hands_counter
                self.lay_on_hands_counter = 0
            self.action = 0
            self.DM.say(self.name + ' uses lay on hands', True)
            target.changeCHP(dmg(-1*heal, 'heal'), self, False)

    def use_empowered_spell(self):
        rules = [self.knows_empowered_spell, self.sorcery_points > 0, self.empowered_spell==False]
        errors= [
            self.name + ' tried to use Empowered Spell without knowing it',
            self.name + ' tried to use empowered Spell, but has no Sorcery Points left',
            self.name + ' tried to use empowered spell, but has already used it']
        ifstatements(rules, errors, self.DM).check()

        self.sorcery_points -= 1
        self.empowered_spell = True
        self.DM.say(self.name + ' used Empowered Spell', True)

    def use_action_surge(self):
        rules = [self.knows_action_surge,
            self.action_surge_counter > 0,
            self.action_surge_used == False]
        errors = [
            self.name + ' tried to use action surge, but does not know how',
            self.name + ' tried to use action surge, but has no charges left',
            self.name + ' tried to use action surge, but already used it']
        ifstatements(rules, errors, self.DM).check()

        self.action_surge_counter -= 1
        self.action_surge_used = True
        self.action_surge()      #This resets the action, cast and attacks
        self.DM.say(self.name + ' used action surge', True)

    def use_aura_of_protection(self, allies):
        #passiv ability, restes at start of Turn or if unconscious
        if self.knows_aura_of_protection:
            if len(allies) > 5: #at least 5 allies
                targetnumber = int(random() + 2.2) #2-3 plus self
            elif len(allies) > 2:  #at least 2 allies and self
                targetnumber = int(random() + 0.8)  #0-1
            else:
                targetnumber = 0 #only self
            if self.level >= 18: targetnumber += 1 #30ft at lv 18

            #Now choose random targtes plus self
            targets = []
            targets.append(self)
            AllyChoice = [ally for ally in allies if ally != self]
            shuffle(AllyChoice)
            for i in range(0,targetnumber):
                if i >= len(AllyChoice): break #no allies left
                targets.append(AllyChoice[i])
            targets.append(self) #always in aura

            #Now apply Bonus
            links = []
            auraBonus = self.modifier[5] #wis mod 
            for ally in targets:
                links.append(ProtectionAuraToken(ally.TM, auraBonus)) #a link for every Ally
            EmittingProtectionAuraToken(self.TM, links)
        else: return

    def protection_aura(self):
        #Returns the current Bonus of all Auras of Protection 
        AuraBonus = 0
        if self.TM.checkFor('aop') == True: #Check if you have a aura of protection Token
            for x in self.TM.TokenList:
                if x.subtype == 'aop':
                    if x.auraBonus > AuraBonus: # mag. effects dont stack, take stronger effect
                        AuraBonus += x.auraBonus #take the Aura Bonus from Token
        return AuraBonus

    def use_second_wind(self):
        rules = [self.bonus_action==1, self.knows_second_wind, self.has_used_second_wind == False]
        errors = [self.name + ' tried to use second wind without a BA',
            self.name + ' tried to use second wind without knowing it',
            self.name + ' tried to use second wind, but has used it already']
        ifstatements(rules, errors, self.DM).check()

        heal = 5.5 + self.level
        self.DM.say(self.name + ' used second wind', True)
        self.changeCHP(dmg(-heal,'heal'), self, was_ranged=False)
        self.bonus_action = 0
        self.has_used_second_wind = True #until end of fight

    def use_turn_undead(self, targets):
        rules = [self.knows_turn_undead,
                self.action > 0,
                self.channel_divinity_counter > 0]
        errors = [self.name + ' tried to use turn undead, but ' + 'does not know how',
                self.name + ' tried to use turn undead, but ' + 'has no action left',
                self.name + ' tried to use turn undead, but ' + 'has no channel divinity left']
        ifstatements(rules, errors, self.DM).check()

        self.DM.say(self.name + ' uses turn undead:', True)
        for target in targets:
            if target.type == 'undead':
                if target.make_save(4, DC = self.spell_dc) < self.spell_dc:
                    #Destroy undead
                    if target.level <= self.destroy_undead_CR:
                        self.DM.say(target.name + ' is destroyed', True)
                        target.death()
                    else:
                        target.is_a_turned_undead = True
                        self.DM.say(target.name + ' is turned', True)
            else:
                continue
        self.action = 0
        self.channel_divinity_counter -= 1 #used a channel divinity

    def use_start_of_turn_heal(self):
        if self.start_of_turn_heal <= 0:
            print(self.name + ' tried to use start of turn heal without having it')
            quit()
        elif self.state != 1:
            return  #not consious
        else:
            self.DM.say(self.name + ' uses regeneration', True)
            heal = dmg(-self.start_of_turn_heal, type='heal')
            self.changeCHP(heal, self, was_ranged=False)

    def summon_primal_companion(self, fight):
        rules = [
            self.knows_primal_companion, #has the Ability
            self.used_primal_companion == False #has not used this fight
        ]
        errors = [
            self.name + ' tried to summon primal companion but has none',
            self.name + ' tried to summon primal companion but used it before'
        ]
        ifstatements(rules, errors, self.DM).check()
        companion = self.summon_entity('Primal Companion', archive=True)
        companion.name = ''.join([self.name, 's Companion'])
        companion.team = self.team  #your team
        #AC
        companion.AC = 13 + self.proficiency
        companion.shape_AC = companion.AC
        companion.base_AC = companion.AC
        #Stats
        companion.HP = 5 + 5*self.level
        companion.CHP = companion.HP
        companion.proficiency = self.proficiency
        #Attack
        companion.tohit = self.spell_mod + self.proficiency
        companion.base_tohit = companion.tohit
        companion.dmg = 6.5 + self.proficiency
        companion.base_dmg = companion.dmg
        if self.knows_beastial_fury:  #double attacks Beast
            companion.base_attacks = 2
            companion.attacks = companion.base_attacks
            companion.attack_counter = companion.base_attacks
        #actions
        companion.AI.Choices = [companion.AI.dodgeChoice]  #It can only act if player uses BA, or dodge
        companion.summoner = self  #the player is this companions summoner

        fight.append(companion) #Add companion to the fight
        self.primal_companion = companion

        if self.AI.primalCompanionChoice not in self.AI.Choices:
            self.AI.Choices.append(self.AI.primalCompanionChoice) #activate this choice, to attaack with companion 
        PrimalBeastMasterToken(self.TM, PrimalCompanionToken(companion.TM, subtype='prc')) #The Token will resolve if one of them dies
        self.DM.say(self.name + ' summons its primal companion', True)
        self.used_primal_companion = True #used it once 

    def use_favored_foe(self, target):
        rules = [
            self.knows_favored_foe, #has the Ability
            self.favored_foe_counter > 0, #has counter left
            self.is_concentrating == False 
        ]
        errors = [
            self.name + ' tried to use fav foe without knowing it',
            self.name + ' tried to use fav foe without uses left',
            self.name + ' tried to use fav foe while concentrating'
        ]
        ifstatements(rules, errors, self.DM).check()

        self.DM.say(''.join([self.name, ' marked ', target.name, ' as favored foe']), True)
        FavFoeToken(self.TM, FavFoeMarkToken(target.TM, subtype='fm')) #mark target as fav foe
        self.favored_foe_counter -= 1

    def use_deflect_missiles(self, target, Dmg, wants_to_return_attack):
        #Check if this is allowed
        rules = [
            self.knows_deflect_missiles,
            self.reaction == 1
        ]
        errors = [
            self.name + ' tried to use deflect missiles without knowing it',
            self.name + ' tried to use deflect missiles but already used their reaction'
        ]
        ifstatements(rules, errors, self.DM).check()

        #Reduce dmg
        self.DM.say(''.join([self.name, ' deflected ', target.name, '\'s ranged attack']), True)
        self.reaction = 0
        Dmg.substract(5 + self.modifier[1] + self.ki_points_base) #this will reduce the dmg later when dmg is calculated and changed in changeCHP
        #Wants to return Attack?
        if wants_to_return_attack:
            if Dmg.abs_amount() < 1 and self.ki_points > 0: #You can return attack
                self.DM.say(''.join([self.name, ' catches and redirects ', target.name, '\'s missile back at them!']), True)
                self.ki_points -= 1
                self.attack(target, is_ranged=True) #Make an ranged attack

    def use_stunning_strike(self, target):
        rules = [
            self.knows_stunning_strike,
            self.ki_points >= 1
        ]
        errors = [
            self.name + ' tried to use stunning strike without knowing it.',
            self.name + ' tried to use stunning strike but is out of ki points.'
        ]
        ifstatements(rules, errors, self.DM).check()
        self.DM.say(''.join([self.name, ' used stunning strike, ', target.name]), True)
        self.ki_points -= 1
        if target.make_save(2, DC = self.ki_save_dc) < self.ki_save_dc:
            LinkToken = StunningStrikedToken(target.TM)
            StunningStrikeActive(self.TM, [LinkToken])
            self.DM.say(''.join([target.name, ' failed their saving throw and is stunned.']), True)
        else:
            self.DM.say(''.join([target.name, ' passed their saving throw and avoided being stunned.']), True)

#---------------Spells---------------
    def check_for_armor_of_agathys(self):
        #This function is called if a player is attacked and damaged in changeCHP
        #If the player has THP left, if calles this function to check if it has armor of agathys
        #If true, this functions return the dmg to the attacker
        AgathysDmg = dmg()
        if self.THP > 0:
            if self.has_armor_of_agathys:
                AgathysDmg.add(self.agathys_dmg, 'cold')
        return AgathysDmg #is 0 if nothig added

    def summon_entity(self, Name, archive=True):
        #This is to initialize a entity
        #For spells like conjure animals
        summon = entity(Name, self.team, self.DM, archive=True)
        return summon



#---------------Round Handling------------
    def start_of_turn(self):
        #Attention, is called in the do the fighting function
        #ONLY called if player state = 1
        self.reckless = 0
        self.stepcounter=0 
        self.attack_counter = self.attacks #must be on start of turn, as in the round an attack of opportunity could have happened, also maybe shape was dropped
        self.AC = self.shape_AC  #reset AC to the AC of the shape (maybe wild shape)
        self.TM.startOfTurn() 

        if self.knows_dragons_breath: #charge Dragons Breath
            if random() > 2/3:
                self.dragons_breath_is_charged = True

        if self.knows_recharge_aoe: #Charge aoe
            if random() < self.aoe_recharge_propability:
                self.recharge_aoe_is_charged = True

        if self.knows_spider_web: #charge Spider Web
            if random() > 2/3:
                self.spider_web_is_charged = True

        if self.is_hasted:#additional Hast attack
            self.attack_counter += 1
            self.AC += 2

        if self.is_a_turned_undead:
            #they can also use dodge, so maybe implement 50/50
            self.action = 0
            self.attack_counter = 0
            self.bonus_action = 0
            self.reaction = 0

        if self.is_incapacitated:
            self.action = 0
            self.attack_counter = 0
            self.bonus_action = 0
            self.reaction = 0
        
        if self.start_of_turn_heal != 0:
            self.use_start_of_turn_heal()

    def action_surge(self):
        self.attack_counter = self.attacks #You can do your attacks again
        self.action = 1      #You get one additional action
        self.has_cast_left = True        #You can cast again in your new action

    def end_of_turn(self):    #resets all round counters
        self.bonus_action = 1
        self.reaction = 1
        if self.is_a_turned_undead or self.is_stunned:
            self.reaction = 0
        self.action = 1
        self.has_cast_left = True
        self.poison_bites = 1
        self.sneak_attack_counter = 1
        self.no_attack_of_opportunity_yet = True
        self.action_surge_used = False
        self.is_attacking = False
        self.has_wolf_mark = False #reset totem of wolf mark

        self.TM.endOfTurn() #Resolve and Count all Tokens

        #If you have not dashed this round, you should not have a dash target anymore
        if self.has_dashed_this_round == False:
            self.dash_target = False
        self.has_dashed_this_round = False #reset for next round

        if self.raged == True:
            self.rage_round_counter += 1 #another round of rage
            if self.rage_round_counter >= 10:
                self.end_rage()
        
        if self.has_spiritual_weapon:
            self.SpiritualWeaponCounter += 1
            if self.SpiritualWeaponCounter >= 10:
                self.break_spiritual_weapon()
                
        if self.is_a_turned_undead:
            self.turned_undead_round_counter += 1
            if self.turned_undead_round_counter >= 10:
                self.end_turned_undead()

        if self.interception_amount != 0:
            self.interception_amount = 0 #no longer in interception
        
        self.chill_touched = False

    def long_rest(self):       #resets everything to initial values
        self.name = self.orignial_name
        self.AC = self.base_AC
        self.shape_AC = self.base_AC
        self.dmg = self.base_dmg
        self.tohit = self.base_tohit
        self.attacks = self.base_attacks
        self.type = self.base_type
        self.damage_type = self.base_damage_type

        for i in range(0, len(self.spell_slots)):
            self.spell_slot_counter[i] = self.spell_slots[i]

        self.break_concentration()
        self.TM.resolveAll()

        self.wailsfromthegrave_counter = self.proficiency
        self.sneak_attack_counter = 1
        self.reckless = 0
        self.raged = 0
        self.rage_round_counter = 0
        self.lay_on_hands_counter = self.lay_on_hands
        self.sorcery_points = self.sorcery_points_base
        self.ki_points = self.ki_points_base
        self.action_surge_counter = self.action_surges
        self.action_surge_used = False
        self.has_used_second_wind = False
        self.has_additional_great_weapon_attack = False
        self.used_primal_companion = False
        self.primal_companion = False
        self.favored_foe_counter = self.proficiency
        self.has_favored_foe = False

        self.dragons_breath_is_charged = False
        self.spider_web_is_charged = False
        self.recharge_aoe_is_charged = False
        self.poison_bites = 1 #restore Poison bite 
        self.legendary_resistances_counter = self.legendary_resistances #regain leg. res.

        self.drop_shape()
        self.is_shape_changed = False
        self.is_in_wild_shape = False
        self.wild_shape_uses = 2
        self.inspired = 0
        self.is_combat_inspired = False
        if self.knows_inspiration:
            self.inspiration_counter = self.base_inspirations
        else:
            self.inspiration_counter = 0

        self.state = 1
        self.death_counter = 0
        self.heal_counter = 0
        self.CHP = self.HP
        self.THP = 0
        self.initiative = 0
        self.attack_counter = self.attacks
        self.position = self.base_position #Go back 
        self.is_attacking = False


        self.modifier = self.base_modifier

        self.action = 1
        self.bonus_action = 1
        self.reaction = 1
        self.has_cast_left = True
        self.is_concentrating = False

        self.restrained = False             #will be ckeckt wenn attack/ed 
        self.prone = 0
        self.is_blinded = False
        self.is_dodged = False
        self.is_stunned = False
        self.is_incapacitated = False
        self.is_paralyzed = False
        self.is_poisoned = False
        self.is_invisible = False


        self.dash_target = False
        self.has_dashed_this_round = False
        self.last_attacker = 0
        self.dmg_dealed = 0
        self.heal_given = 0
        self.unconscious_counter = 0

        #Haste
        self.haste_round_counter = 0    #when this counter hits 10, haste will wear off
        #Hex
        self.can_choose_new_hex = False
        #Hunters Mark
        self.can_choose_new_hunters_mark = False
        #Armor of Agathys
        self.has_armor_of_agathys = False
        self.agathys_dmg = 0
        #Spiritual Weapon
        self.has_spiritual_weapon = False
        self.SpiritualWeaponDmg = 0
        self.SpiritualWeaponCounter = 0
        #Summons
        self.has_summons = False
        #Guiding Bolt
        self.is_guiding_bolted = False
        #TurnUnded
        self.is_a_turned_undead = False
        self.turned_undead_round_counter = 0
        #Interception
        self.interception_amount = 0

        self.empowered_spell = False
        self.quickened_spell = False
    
#-------------Monster Abilities-------------
    def use_dragons_breath(self, targets, DMG_Type = 'fire'):
        #only works if charged at begining of turn
        if self.knows_dragons_breath and self.dragons_breath_is_charged and self.action == 1:
            if type(targets) != list: #maybe only one Element was passed
                targets = [targets]  #make it a list then
            self.DM.say(self.name + ' is breathing fire', True)
            self.dragons_breath_is_charged = False
            for target in targets:
                DragonBreathDC = 12 + self.modifier[2] + int((self.level - 10)/3)  #Calculate the Dragons Breath DC 
                target.last_attacker = self    #target remembers last attacker
                save = target.make_save(1, DC=DragonBreathDC)           #let them make saves
                Dmg = dmg(20 + int(self.level*3.1), DMG_Type)
                if save >= DragonBreathDC:
                    Dmg.multiply(1/2)
                target.changeCHP(Dmg, self, True)
            self.action = 0
        else: 
            print('Dragon breath could not be used')
            quit()

    def use_recharge_aoe(self, targets):
        #only works if charged at begining of turn
        if self.knows_recharge_aoe and self.recharge_aoe_is_charged and self.action == 1:
            if type(targets) != list: #maybe only one Element was passed
                targets = [targets]  #make it a list then
            self.DM.say(self.name + ' uses its recharge AOE', True)
            self.recharge_aoe_is_charged = False
            for target in targets:
                target.last_attacker = self    #target remembers last attacker
                save = target.make_save(self.aoe_save_type, DC = self.aoe_recharge_dc)   #let them make saves
                Dmg = dmg(self.aoe_recharge_dmg, self.aoe_recharge_type)
                if save >= self.aoe_recharge_dc:
                    Dmg.multiply(1/2)
                target.changeCHP(Dmg, self, True)
            self.action = 0
        else: 
            print('Recharge AOE could not be used')
            quit()

    def use_spider_web(self, target):
        if self.knows_spider_web and self.spider_web_is_charged and self.action == 1:
            self.DM.say(self.name + ' is shooting web', True)
            self.spider_web_is_charged = False
            target.last_attacker = self #remember last attacker
            SpiderWebDC = 9 + self.modifier[1] #Dex
            #Shoot Web at random Target
            if target.make_save(1, DC = SpiderWebDC) < SpiderWebDC:
                self.DM.say(target.name + ' is caugth in the web and restrained', True)
                SpiderToken = Token(target.TM)
                SpiderToken.subtype = 'r'  #restrain Target, no break condition yet
            self.action = 0
        else: 
            print('Spider Web could not be used')
            quit()


#Choice

class choice:
    def __init__(self, player):
        self.player = player
        if self.player.DM.AI_blank: #this is only a dirty trick so that VScode shows me the attributes of player and MUST be deactived
            self.player = entity('test', 0, 0)
  
class do_attack(choice):
    def __init__(self, player):
        super().__init__(player)
        self.is_offhand = False
    
    def score(self, fight):
        #This function return a damage equal value, that should represent the dmg that could be expected form this player if it just attacks
        player = self.player
        Score = 0
        #No attack possible return 0
        #Action Attack:
        if self.is_offhand == False:
            if player.action == 0: return 0
            elif player.attack_counter < 1: return 0
            dmg = player.dmg
            attacks = player.attacks
            if (player.knows_rage and player.bonus_action == 1) or player.raged == 1:
                dmg += player.rage_dmg
            if player.knows_frenzy:
                attacks += 1
            if player.is_hasted:
                attacks += 1

        #Offhand Attack
        else:
            if player.is_attacking == False: return 0 #didnt attack in action
            dmg = player.offhand_dmg
            attacks = 1
            if dmg == 0: return 0  #no offhand attack if dmg = 0
        
        if player.knows_reckless_attack:
            dmg = dmg*1.2 #improved chance to hit
        if player.restrained or player.is_blinded or player.is_poisoned:
            dmg = dmg*0.8
        if player.is_hexing:
            dmg += 3.5

        #dmg score is about dmg times the attacks
        #This represents vs a test AC
        TestACs = [x.AC for x in fight if x.team != player.team and x.state != -1]
        if len(TestACs) > 0:
            TestAC = np.mean(TestACs)
        else: TestAC = 16
        if TestAC > 20: TestAC = 20 #if one has rediculous high armor
        Score = dmg*(20 - TestAC + player.tohit)/20*attacks

        #Only on one Attack 
        if player.sneak_attack_counter == 1:
            Score += player.sneak_attack_dmg
        if player.wailsfromthegrave_counter > 0:
            Score += player.sneak_attack_dmg/2
        if player.knows_great_weapon_master and self.is_offhand == False:
            Score += 5  #+10 dmg, but no great hit prop
        if player.knows_archery: Score += dmg*0.1 #better hit chance
        if player.knows_great_weapon_fighting: dmg += dmg*0.1 #more dmg
        if player.knows_improved_critical: dmg += dmg*0.1 #better crit
        if player.knows_smite:
            for i in range(0,5):
                if player.spell_slot_counter[4-i] > 0:
                    Score += (4-i)*4.5  #Smite Dmg once
                    break

        #Other Stuff
        if player.dash_target != False: #Do you have a dash target?
            if player.dash_target.state == 1: Score*1.5 #Encourage a Dash target attack
        if player.has_range_attack == False:
            Score = Score*np.sqrt(player.AC/(13 + player.level/3.5)) #Encourage player with high AC
        if Score < 0: Score = 0
        return Score

    def execute(self, fight):
        player = self.player
        #This function then actually does the attack<<
        if player.action == 1: #if nothing else, attack
            if player.knows_reckless_attack:
                player.rackless_attack()
            if player.knows_rage and player.bonus_action == 1 and player.raged == 0:
                player.rage() #includes frenzy
            if player.is_in_frenzy and player.bonus_action == 1:
                player.use_frenzy_attack()
            while player.attack_counter > 0 and player.state == 1:  #attack enemies as long as attacks are free and alive (attack of opportunity might change that)
                target = player.AI.choose_att_target(fight) #choose a target
                if target == False: #there might be no target
                    return
                else:
                    player.make_normal_attack_on(target, fight)  #attack that target

class do_offhand_attack(do_attack):
    def __init__(self, player):
        super().__init__(player)
        self.is_offhand = True
    
    def score(self, fight):
        return super().score(fight)

    def execute(self, fight):
        player = self.player
        #This function does a offhand attack as BA
        if player.bonus_action == 1:
            if player.knows_reckless_attack:
                player.rackless_attack()
            target = player.AI.choose_att_target(fight) #choose a target
            if target == False: #there might be no target
                return
            else:
                player.make_normal_attack_on(target, fight, is_off_hand=True)  #attack that target

class do_dodge(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        if self.player.action == 0: return 0
        else: return 1  #For now
    
    def execute(self, fight):
        self.player.use_dodge()

class do_inspire(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        Score = 0
        if self.player.inspiration_counter == 0: return 0
        if self.player.knows_inspiration == False: return 0
        if self.player.bonus_action != 1: return 0
        if random() > 0.2: Score = self.player.level*2
        if self.player.knows_cutting_words and self.player.inspiration_counter == 1:
            Score = Score/2 #keep last inspiration
        return Score
    
    def execute(self, fight):
        rules = [self.player.knows_inspiration, 
                self.player.inspiration_counter > 0,
                self.player.bonus_action == 1]
        if all(rules):
            allies = [x for x in fight if x.team == self.player.team]
            self.player.inspire(allies[int(random()*len(allies))])

class go_wildshape(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        player = self.player
        if player.knows_wild_shape == False: return 0
        if player.is_shape_changed: return 0
        if player.wild_shape_uses < 1: return 0
        if player.action == 1 or (player.bonus_action == 1 and player.knows_combat_wild_shape):
            Score = player.DruidCR*6*(2 + random()) #CR * about 6 dmg/CR * 2-3 Rounds
            Score += player.HP/(player.CHP + player.HP/4)*Score   #if low on HP go wild shape
            #Up to 4 times the score if very low
            if player.knows_combat_wild_shape:
                Score = Score*1.2  #if you know combat wild shape freaking go
            if player.is_concentrating: Score = Score*1.3 #is really good to go into wild shape with a con spell
            return Score
        else: return 0
    
    def execute(self, fight):
        player =self.player 
        rules = [player.knows_wild_shape,
                player.wild_shape_uses > 0,
                player.is_shape_changed == False,
                player.action == 1 or (player.bonus_action == 1 and player.knows_combat_wild_shape)]
        if all(rules):
            #Check smaller and smaller Margins until you find a suitable but still High Creature
            ChoiceIndex = False
            for i in range(1,5):
                Choices = self.find_forms(1 - i/5)
                if Choices != []:
                    Index = int(random()*len(Choices)) #Random Choice of those available
                    ChoiceIndex = Choices[Index] #Thats the Form Choosen
                    break
            self.player.wild_shape(ChoiceIndex)

    def find_forms(self, Margin):
        #This function returns an Index List for the Beast Forms
        #The returned forms are smaller then Cr but highter then Margin*CR
        #Marget like 80% from CRmax: 0.8
        BeastForms = self.player.BeastForms
        FormList = [i for i in BeastForms if BeastForms[i]['Level'] <= self.player.DruidCR and BeastForms[i]['Level'] >= self.player.DruidCR*Margin]
        return FormList        

class use_action_surge(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        if self.player.knows_action_surge == False: return 0
        if self.player.action_surge_counter == 0: return 0
        if self.player.action_surge_used: return 0
        if self.player.action == 1: return 0 #no use if action is 1
        if self.player.CHP/self.player.HP < 0.6:
            return self.player.dps() #action surge is good and cost nothing
        return 0
    
    def execute(self, fight):
        self.player.use_action_surge()
        self.player.AI.do_your_turn(fight) #use action surge and start turn again

class do_spiritual_weapon(choice):
    def __init__(self, player):
        super().__init__(player)

    def score(self, fight):
        if self.player.has_spiritual_weapon == False: return 0
        if self.player.bonus_action == 0: return 0
        return self.player.SpiritualWeaponDmg
    
    def execute(self, fight):
        player = self.player
        target = player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=player.SpiritualWeaponDmg, other_dmg_type='force', is_silent=True)
        if target != False:
            player.SpellBook['SpiritualWeapon'].use_spiritual_weapon(target)
        else: player.bonus_action = 0

class do_turn_undead(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self,fight):
        if self.player.knows_turn_undead == False: return 0
        if self.player.channel_divinity_counter < 1: return 0
        if self.player.action == 0: return 0

        Score = sum([x.dps() for x in fight if x.type == 'undead' and x.state == 1])
        if 'undead' in [x.type for x in fight if x.team == self.player.team]:
            #dont use if teammates undead
            Score = 0
        return Score

    def execute(self,fight):
        targets = self.player.AI.area_of_effect_chooser(fight, 2500)
        self.player.use_turn_undead(targets)

class do_spellcasting(choice):
    def __init__(self, player):
        super().__init__(player)
        self.SpellScore = 0
        self.ChoosenSpell = False
    
    def score(self, fight):
        player = self.player
        self.SpellScore = 0
        self.ChoosenSpell = False

        if len(player.SpellBook) > 0:# check if player knows any spells
            if player.bonus_action == 1 or player.action == 1: #if you have still action left 
                #print(self.choose_spell(fight))
                self.ChoosenSpell, self.SpellScore = player.AI.choose_spell(fight)
        return self.SpellScore
    
    def execute(self, fight):
        player = self.player
        #Empowered Spell, if you have sorcery Points
        if player.sorcery_points > 2 and player.empowered_spell == False and player.knows_empowered_spell:
            Score = 0
            #Encourage for low HP
            if player.CHP < player.HP/2: Score += 10
            if player.CHP < player.HP/3: Score += 10
            if player.CHP < player.HP/4: Score += 10
            #Disencourage for low SP
            Score -= (1-player.sorcery_points/player.sorcery_points_base)*15
            Score = Score*(random()/2 + 0.75)
            if Score > 10:
                player.use_empowered_spell()
        if self.ChoosenSpell != False:
            self.ChoosenSpell() #cast choosen Spell

class use_ki(choice):
    def __init__(self, player):
        super().__init__(player)

    def score(self, fight):
        player = self.player
        if player.ki_points == 0: return 0
        Score = 0

        # if player.

    def execute(self, fight):
        player = self.player

    #ki point priority in descending order of score/priority: stunning strike (prioritize strong enemy), flurry of blows (if have open hand technique, ++score, prob always before stunning strike), deflect missiles (conditional, see entity class), step of the wind, patient defense

class do_monster_ability(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        player = self.player
        if player.action == 0: return 0
        Score = 0

        if player.dragons_breath_is_charged:
            Score += (20 + int(player.level*3.1))*3   #damn strong ability, at least 2-3 Targets
        if player.recharge_aoe_is_charged:
            Score += player.aoe_recharge_dmg*2 #might hit 2-3 targts
        if player.spider_web_is_charged:
            Score += player.dmg*player.attacks*1.5   #good Ability, better then simple attack
        return Score
    
    def execute(self, fight):
        player = self.player
        if player.knows_recharge_aoe and player.action == 1:
            if player.recharge_aoe_is_charged:
                self.recharge_aoe(fight)
        #Dragon Breath
        if player.knows_dragons_breath and player.action == 1:
            if player.dragons_breath_is_charged:
                self.dragons_breath(fight)
        #Spider Web
        if player.knows_spider_web and player.action == 1:
            if player.spider_web_is_charged:
                self.spider_web(fight)

    def recharge_aoe(self, fight):
        player = self.player
        targets = player.AI.area_of_effect_chooser(fight, player.aoe_recharge_area)
        if len(targets) == len([x for x in fight if x.team != player.team]) and len(targets) > 1:
            max = int(len(targets)*0.5 + 0.5) #some should be able to get out, even for high area of effect
            targets = targets[0:-1*max]
        player.use_recharge_aoe(targets)

    def dragons_breath(self, fight):
        player = self.player
        if player.level < 10: area = 250
        elif player.level < 15: area = 450 
        elif player.level < 20: area = 1800 #60-ft-cone
        else: area = 4000 #90-ft-cone
        targets = player.AI.area_of_effect_chooser(fight, area)
        if len(targets) == len([x for x in fight if x.team != player.team]) and len(targets) > 1:
            max = int(len(targets)*0.5 + 0.5) #some should be able to get out, even for high are of effect
            targets = targets[0:-1*max]
        player.use_dragons_breath(targets)
    
    def spider_web(self, fight):
        player = self.player
        enemies_left = [x for x in fight if x.team != player.team and x.state == 1]
        #Random Target
        if len(enemies_left) > 0:
            player.use_spider_web(enemies_left[int(random()*len(enemies_left))])
        else:
            #No enemies left
            player.action = 0 #use acrion, nothing left to attack

class attack_with_primal_companion(choice):
    def __init__(self, player):
        super().__init__(player)

    def score(self, fight):
        if self.player.primal_companion == False: return 0
        companion = self.player.primal_companion
        if companion.state != 1: return 0
        if self.player.bonus_action == 0: return 0
        if self.player.primal_companion.action == 0: return 0
        if self.player.primal_companion.attack_counter <= 0: return 0
        return (companion.dmg + companion.value())/2*companion.attacks
    
    def execute(self, fight):
        companion = self.player.primal_companion
        rules = [
            companion != False,
            companion.attack_counter > 0,
            companion.action == 1,
            companion.state == 1,
            self.player.bonus_action == 1
        ]
        if all(rules):
            while companion.attack_counter > 0 and companion.state == 1:  #attack enemies as long as attacks are free and alive (attack of opportunity might change that)
                target = companion.AI.choose_att_target(fight) #choose a target
                if target == False: #there might be no target
                    return
                else:
                    companion.make_normal_attack_on(target, fight)  #attack that target
            self.player.bonus_action = 0

class do_heal(choice):
    def __init__(self, player):
        super().__init__(player)
    
    def score(self, fight):
        player = self.player
        self.has_heal = False
        self.HealTarget = False

        #Check for heal
        if player.lay_on_hands_counter > 0 and player.action == 1:
            self.has_heal = True
        if 'CureWounds' in player.SpellBook:
            if player.AI.spell_cast_check(player.SpellBook['CureWounds']) != False:
                self.has_heal = True
        if 'HealingWord' in player.SpellBook:
            if player.AI.spell_cast_check(player.SpellBook['HealingWord']) != False:
                self.has_heal = True

        if self.has_heal == False: return 0
        else:
            #if the player has heal, check what target would be good
            self.HealTarget, HealScore = self.choose_heal_target(fight)
            if player.CHP < player.HP/4: HealScore += player.value()/3 #encourage if low
            if self.HealTarget != False: return HealScore
            else: return 0

    def choose_heal_target(self, fight):
        #This function is called if the player has heal
        #It returns the best Target for a heal and gives the Heal a Score
        #If False is returned, Heal will not be added as a Choice for this turn
        player = self.player
        self.allies = [x for x in fight if x.team == player.team and x.state != -1]
        self.dying_allies = [x for x in self.allies if x.state == 0]
        if self.dying_allies != []:      #someone is dying
            DyingScore = []
            for ally in self.dying_allies:
                Score = ally.dps()*ally.death_counter #High Score for a high death_counter
                Score += ally.value()
                Score = Score*0.7*(0.8+random()*0.4) #little random power
                if ally.chill_touched: Score = 0 #can not be healed
                #The Score will be returned as a Score for the Choices in do_your_turn too
                DyingScore.append(Score)
            MaxIndex = np.argmax(DyingScore)
            Target = self.dying_allies[MaxIndex]
            return Target, DyingScore[MaxIndex]
        #No One is currently dying
        else:
            TeamHP = sum([x.HP for x in self.allies])
            TeamCHP = sum([x.CHP for x in self.allies])
            if TeamCHP/TeamHP < 0.7:
                HealScores = []
                for ally in self.allies:
                    Score = ally.value()*2/3 #Player is not dead, might still do another round
                    Score = Score*(1 - ally.CHP/ally.HP) #Score Scales with CHP left
                    Score = Score*(0.8+random()*0.4)
                    if ally.CHP/ally.HP > 0.6:
                        Score = 0
                    HealScores.append(Score)
                MaxIndex = np.argmax(HealScores)
                if HealScores[MaxIndex] > player.value()/3: #Minimum Boundry for reasonable heal
                    return self.allies[MaxIndex], HealScores[MaxIndex]
                else:
                    return False, 0
            else:
                return False, 0

    def execute(self, fight):
        #This function is called as an AI Coice
        #If it is is called there should be a heal option aviable for the player
        #Also the Choose Heal Target function should already assigned a heal target
        #The only thing to choose now is what king of Healing and how much, which SpellSlot 
        player = self.player
        target = self.HealTarget

        #self is low, heal yourself instead if target
        if player.CHP < int(player.HP/4) and player.lay_on_hands_counter > player.lay_on_hands/2 and player.action == 1:
            player.use_lay_on_hands(player, player.lay_on_hands_counter - int(player.lay_on_hands_counter/5))
            return

        #Choose Heal
        HealingWordValue = 0
        CureWoundsValue = 0
        if 'HealingWord' in player.SpellBook:
            HealingWordValue = player.AI.spell_cast_check(player.SpellBook['HealingWord'])
        if 'CureWounds' in player.SpellBook:
            CureWoundsValue = player.AI.spell_cast_check(player.SpellBook['CureWounds'])
        level = self.player.AI.choose_heal_spellslot(MinLevel=1)
        if HealingWordValue == 1: #HealingWord is castable
            player.SpellBook['HealingWord'].cast(target, cast_level=level)
        elif player.lay_on_hands_counter > 0 and player.action ==1:
            player.use_lay_on_hands(target, 5)
        elif CureWoundsValue == 1: #HealingWord is castable
            player.SpellBook['CureWounds'].cast(target, cast_level=level)
        elif HealingWordValue == 2: #HealingWord via Quickened Spell
            player.SpellBook['HealingWord'].quickened_cast(target, cast_level=level)
        elif CureWoundsValue == 2: #HealingWord via Quickened Spell
            player.SpellBook['CureWounds'].quickened_cast(target, cast_level=level)
        else:
            #This should not happen
            print('This is stupid, no Heal in AI, check do_heal class')
            quit() 

class do_call_lightning(choice):
    def __init__(self, player):
        super().__init__(player)

    def score(self, fight):
        #This Score only apllies to the re-casting of the Spell, not the initial cast
        #Tis is the reason why this score is rather generously calculated, to encourage using this
        if self.player.action == 0: return 0
        recastDmg = self.player.SpellBook['CallLightning'].recast_damge  #recast dmg saved in spell at the last cast
        Score = 0
        Score = recastDmg*(1.5+random()) #dmg*1.5-2.5 targets
        Score += 10 #a little bonus to encourage recasting this, because it does not cost extra cast
        return Score
    
    def execute(self, fight):
        #Use action to recast spell
        player = self.player
        area = self.player.SpellBook['CallLightning'].aoe_area
        #Choose Targets
        targets = self.player.AI.area_of_effect_chooser(fight, area=area)

        self.player.SpellBook['CallLightning'].recast(targets) #recast, sets action = 0

class AI:
    def __init__(self, player):
    #this class is initialized in the Entity class to controll all the moves and decisions
        self.player = player
        if self.player.DM.AI_blank: #this is only a dirty trick so that VScode shows me the attributes of player and MUST be deactived
            self.player = entity('test', 0, 0)

        #this is later filled in do_your_turn()
        self.allies = [] #only Allies left alive
        self.dying_allies = []

        #---------TEST---------
        self.Choices = [
            do_attack(player),
            do_offhand_attack(player),
            do_monster_ability(player),
            do_heal(player),
            do_dodge(player)
        ]
        if len(self.player.SpellBook) > 0:
            self.Choices.append(do_spellcasting(player))#if any Spell is known, add this choice option
        if self.player.knows_inspiration:
            self.Choices.append(do_inspire(player))
        if self.player.knows_action_surge:
            self.Choices.append(use_action_surge(player))
        if self.player.knows_turn_undead:
            self.Choices.append(do_turn_undead(player))
        if self.player.knows_wild_shape:
            self.Choices.append(go_wildshape(player))

        #Conditional Choices        
        self.spiritualWeaponChoice = do_spiritual_weapon(player) #This will be later added to the Choices list, if a Character casts spiritual weapon
        self.primalCompanionChoice = attack_with_primal_companion(player) #This Choice is added if a primal companion is summoned
        self.callLightningChoice = do_call_lightning(player) #This Choice is added (and removed later) by the call lightning spell token
        self.dodgeChoice = do_dodge(player) #Is needed as choice for primal companion

        self.conditionalChoicesList = [self.callLightningChoice]

    def do_your_turn(self,fight):
        player = self.player
        self.allies = [x for x in fight if x.team == player.team and x.state != -1]       #which allies
        self.dying_allies = [i for i in self.allies if i.state == 0]     #who is dying

        #stand up if prone
        if player.prone == 1 and not (player.restrained or player.is_stunned or player.is_paralyzed):
            player.stand_up()
        
        #Summon Primal Companion if you have
        if player.knows_primal_companion:
            if player.used_primal_companion == False:
                player.summon_primal_companion(fight)

        #Choosing Aura of Protection Targets:
        if player.knows_aura_of_protection: player.use_aura_of_protection(self.allies)

        #Choose new Hex
        if player.can_choose_new_hex: self.choose_new_hex(fight)
        if player.can_choose_new_hunters_mark: self.choose_new_hunters_mark(fight)

        #Concentration Spells
        if player.is_concentrating:
            self.do_concentration_spells(fight)

        #Use Second Wind
        if player.knows_second_wind and player.has_used_second_wind == False:
            if player.bonus_action == 1:
                if player.CHP/player.HP < 0.3: player.use_second_wind()

        #Interception
        if player.knows_interception:
            self.allies[int(random()*len(self.allies))].interception_amount = 5.5 + player.proficiency

        #------------Not in alternate Shape
        if player.is_shape_changed == False:
        #--------Evaluate Choices
            while (player.action == 1 or player.bonus_action == 1) and player.state == 1:
                EnemiesConscious = [x for x in fight if x.state == 1 and x.team != player.team]
                if len(EnemiesConscious) == 0:
                    player.DM.say('All enemies defeated', True)
                    return #nothing left to do
                
                ChoiceScores = [choice.score(fight) for choice in self.Choices] #get Scores
#                print(ChoiceScores)
#                print(self.Choices)
                ActionToDo = self.Choices[np.argmax(ChoiceScores)]
                if np.max(ChoiceScores) > 0:
                    ActionToDo.execute(fight) #Do the best Choice
                #First Round Action and Attacks
                #Secound Round Bonus Action
                #Check if still smth to do, else return
                if sum(ChoiceScores) == 0:
                    rules = [player.bonus_action == 1 and player.action == 1,
                        player.attack_counter > 0,
                        len([x for x in fight if x.team != player.team and x.state == 1]) == 0]
                    if all(rules):
                        player.DM.say(player.name + ' count not decide what to do!', True)
                        quit()
                    return

        #------------Still in Wild Shape
        elif player.is_in_wild_shape: self.smart_in_wildshape(fight) #Do wild shape stuff
        else: self.smart_in_changed_shape(fight) #Just use your shapes attacks

    def do_concentration_spells(self, fight):
        #This function is called at start of turn if the player has a concentration Spell up
        player = self.player

        #Cloud Kill
        if player.is_cloud_killing:
            #Choose new targets
            targets = self.area_of_effect_chooser(fight, area=1250)
            #What Spell Slot
            for token in self.player.TM.TokenList:
                if token.subtype == 'ck': #cloud kill
                    castLevel = token.castLevel #find cast level
                    break
            #recast cloud kill
            player.SpellBook['Cloudkill'].recast(targets, castLevel)

        #Sickening Radiance
        if player.is_using_sickening_radiance:
            #Choose new targets
            targets = self.area_of_effect_chooser(fight, area=2800)
            #recast cloud kill
            player.SpellBook['SickeningRadiance'].recast(targets)

    def add_choice(self, newChoice):
        #This function is intended to add choices, which are conditional
        #This can happen for spells that enable a choice, via their token mybe
        #It checks for a list of Choices that are expected to be added and removed, does not work for others
        if newChoice not in self.conditionalChoicesList:
            print(self.player + ' tried to add a choice (' + str(newChoice) + ') from AI that is not conditional')
            quit()
        if newChoice in self.Choices:
            print(self.player + ' tried to add a choice (' + str(newChoice) + ') to AI that is already in Choices')
            quit()
        self.Choices.append(newChoice)

    def remove_choice(self, oldChoice):
        #This function is intended to remove choices, which are no longer needed
        #This can happen for spells that enable a choice, if their token is resolved
        #It checks for a list of Choices that are expected to be added and removed, does not work for others
        if oldChoice not in self.conditionalChoicesList:
            print(self.player + ' tried to remove a choice (' + str(oldChoice) + ') from AI that is not conditional')
            quit()
        if oldChoice not in self.Choices:
            print(self.player + ' tried to remove a choice (' + str(oldChoice) + ') from AI that is not in Choices')
            quit()
        self.Choices.remove(oldChoice)

#-----------Smart Actions
    def smart_in_wildshape(self, fight):
        player = self.player
        #This function is called in do_your_turn if the player is still in wild shape
        if self.dying_allies != []:
        #is someone dying
            dying_allies_deathcounter = np.array([i.death_counter for i in self.dying_allies])
            if np.max(dying_allies_deathcounter) > 1:
                if 'CureWounds' in player.SpellBook and sum(player.spell_slot_counter) > 0 and player.bonus_action == 1 and player.raged == False:
                    player.wild_reshape()
                    target = self.dying_allies[np.argmax(dying_allies_deathcounter)]
                    for i in range(0,9):
                        if player.spell_slot_counter[i]>0:
                            player.SpellBook['CureWounds'].cast(target, cast_level=i+1)
                            break  
                    self.do_your_turn(fight) #this then starts the healing part again

        #Heal in combat wild shape
        self.try_wild_shape_heal()
        if player.action == 1:
            do_attack(player).execute(fight)
    
    def try_wild_shape_heal(self):
        player = self.player
        if player.knows_combat_wild_shape and player.bonus_action == 1:
            #if wild shape is low < 1/4
            if player.is_in_wild_shape and player.shape_HP < 10:
                #Still have spell slots?
                MaxSlot = self.choose_highest_slot(1,9)
                if MaxSlot == False: return
                SpellSlot = self.choose_highest_slot(1, MaxSlot - 2) #Dont use high spell slots
                if SpellSlot == False: return #no low slots left
                player.use_combat_wild_shape_heal(spell_level=SpellSlot)

    def smart_in_changed_shape(self, fight):
        player = self.player
        #This function is called in do_your_turn if the player is still in alternate shape
        if player.action == 1:
            do_attack(player).execute(fight)

#---------Reaction and choices
    def do_opportunity_attack(self,target):
        #this function is called when the player can do an attack of opportunity
        if target.knows_cunning_action and target.bonus_action == 1:
            target.use_disengage() #use cunning action to disengage
            return
        else:
            if self.player.has_range_attack: is_ranged = True
            else: is_ranged = False
            self.player.attack(target, is_ranged, is_opportunity_attack = True, is_spell=False)

    def want_to_cast_shield(self, attacker, damage):
        #This function is called in the attack function as a reaction, if Shild spell is known
        if all([self.player.CHP < damage.abs_amount(), self.player.raged == False, self.player.is_shape_changed == False]):
            for i in range(9):
                if self.player.spell_slot_counter[i] > 0:
                    self.player.SpellBook['Shield'].cast(target=False, cast_level=i+1)   #spell level is i + 1
                    break

    def want_to_use_great_weapon_master(self, target, advantage_disadvantage):
        #Is called from the attack function if you can use the great weapon feat
        #take -5 to attack and +10 to dmg
        #advantage_disadvanteage > 0 - advantage, < 0 disadv.

        hitPropability = (20 - target.AC + self.player.tohit)/20
        hitPropabilityGWM = (20 - target.AC + self.player.tohit - 5)/20

        def hitPropabilityAdvantage(hitProp, advantage):
            if advantage > 0: #has to get it once out of two
                return 1 - (1-hitProp)**2
            if advantage < 0:  #disadvantage, has to succ twice
                return hitProp**2
            else: return hitProp

        #Calcualte the expectation value for the dmg
        dmgNoGWM = self.player.dmg*hitPropabilityAdvantage(hitPropability, advantage_disadvantage)
        dmgWithGWM = (self.player.dmg + 10)*hitPropabilityAdvantage(hitPropabilityGWM, advantage_disadvantage)
        if dmgWithGWM >= dmgNoGWM : return True
        else: return False

    def want_to_use_smite(self, target):
        #This function is called if an attack hit
        #It should return False or a spell slot to use smite

        if self.player.dmg > target.CHP: return False #is enough
        if 'radiant' in target.damage_immunity: return False
        return self.choose_highest_slot(1,4) #over lv4 slot does not increase dmg

    def want_to_use_favored_foe(self, target):
        #more here pls
        return True

    def want_to_use_deflect_missiles(self, target, Dmg):
        #determines if player wants to reduce dmg with reaction
        #and if so, if it also wants to return attack if possible
        #Must return two boolean in that order
        wants_to_reduce_dmg = True
        wants_to_return_attack = False

        Score = 5 + self.player.modifier[1] + self.player.ki_points_base #Baseline is the amount of reduction dmg
        x = self.player.CHP / self.player.HP
        Score = Score * (3/(np.exp((x - 0.2)*10) + 1) + 1) #This factor starts at 1, at about 0.4 to 0 CHP/HP it goes steeply to about 3.5
        #We are scaling the likelihood of using reaction based on current HP vs max, making much more likely below 50% hp[add graph of function to docs]
        if Score > self.player.dmg: #compare score to player.dmg as dmg would be dealed at opp.attack
            wants_to_return_attack = True
        if Dmg.abs_amount() >= self.player.CHP:
            wants_to_return_attack = True #If you would die, always use the feature
        return wants_to_reduce_dmg, wants_to_return_attack #return two boolean

#---------Support
    def area_of_effect_chooser(self, fight, area):   #area in square feet
    #The chooser takes all enemies and chooses amoung those to hit with the area of effect
    #every target can only be hit once, regardless if it is alive or dead 
    #how many targets wil be hit depends on the area and the density in that area from the Battlefield.txt
        enemies = [x for x in fight if x.team != self.player.team and x.state != -1]
        DensityFaktor = 2
        if self.player.DM.density == 0: DensityFaktor = 1
        elif self.player.DM.density == 2: DensityFaktor = 3
        target_pool = (area/190)**(1/3)*DensityFaktor - 0.7   #how many enemies should be in that area
        #0 is wide space
        #1 is normal
        #2 is crowded


        if target_pool < 1: target_pool = 1     #at least one will be hit 
        if target_pool < 2 and area > 100 and len(enemies) > 3: 
            if random() > 0.6 - area/500:
                target_pool = 2 #usually easy to hit 2
        elif target_pool == 2 and area > 300 and len(enemies) > 6: target_pool = 3

        if target_pool > len(enemies)*0.8 and len(enemies) > 2: #will rarely hit all
            target_pool = target_pool*0.7
        
        target_pool = target_pool*(random()*0.64 + 0.63) + 0.5 #a little random power 
        target_pool += len(enemies)/12*(0.15 + random()*0.55)

        target_pool = int(target_pool)
        shuffle(enemies)
        if len(enemies) < target_pool:
            targets = enemies
        else:
            targets = enemies[0:target_pool]

        #This returns: 
        # 3 ebemies
        #    115: [1000.    0.    0.    0.    0.    0.    0.    0.    0.    0.]
        #    300: [366. 634.   0.   0.   0.   0.   0.   0.   0.   0.]
        #    450: [145. 767.  88.   0.   0.   0.   0.   0.   0.   0.]
        #    800: [254. 746.   0.   0.   0.   0.   0.   0.   0.   0.]
        #    1250: [ 40. 717. 243.   0.   0.   0.   0.   0.   0.   0.]
        #    4000: [  0. 133. 867.   0.   0.   0.   0.   0.   0.   0.]
        # 4 enemies
        #    115: [521. 393.  86.   0.   0.   0.   0.   0.   0.   0.]
        #    300: [161. 719. 120.   0.   0.   0.   0.   0.   0.   0.]
        #    450: [ 83. 769. 148.   0.   0.   0.   0.   0.   0.   0.]
        #    800: [  0. 463. 537.   0.   0.   0.   0.   0.   0.   0.]
        #    1250: [  0. 213. 512. 275.   0.   0.   0.   0.   0.   0.]
        #    4000: [  0. 125. 472. 403.   0.   0.   0.   0.   0.   0.]


        return targets

    def player_attack_score(self, fight, is_offhand=False):
        #This function return a damage equal value, that should represent the dmg that could be expected form this player if it just attacks
        player = self.player
        Score = 0
        if is_offhand:
            dmg = player.offhand_dmg
            attacks = 1
        else:
            dmg = player.dmg
            attacks = player.attacks

        if is_offhand == False:
            if (player.knows_rage and player.bonus_action == 1) or player.raged == 1:
                dmg += player.rage_dmg
            if player.knows_frenzy:
                attacks += 1
            if player.is_hasted:
                attacks += 1

        if player.knows_reckless_attack:
            dmg = dmg*1.2 #improved chance to hit
        if player.restrained or player.is_blinded or player.is_poisoned: #decreases Chance to hit
            dmg = dmg*0.8
        if player.is_hexing:
            dmg += 2+player.attacks
        if player.is_hunters_marking:
            dmg += 2+player.attacks

        #dmg score is about dmg times the attacks
        #This represents vs a test AC
        TestACs = [x.AC for x in fight if x.team != player.team and x.state != -1]
        if len(TestACs) > 0:
            TestAC = np.mean(TestACs)
        else: TestAC = 16
        Score = dmg*(20 - TestAC + player.tohit)/20*attacks

        #Only on one Attack 
        if player.sneak_attack_counter == 1:
            Score += player.sneak_attack_dmg
        if player.wailsfromthegrave_counter > 0:
            Score += player.sneak_attack_dmg/2
        if player.knows_smite:
            for i in range(0,5):
                if player.spell_slot_counter[4-i] > 0:
                    Score += (4-i)*4.5  #Smite Dmg once

        #Other Stuff
        if player.dash_target != False: #Do you have a dash target?
            if player.dash_target.state == 1: Score*1.5 #Encourage a Dash target attack
        if player.has_range_attack == False:
            Score = Score*np.sqrt(player.AC/(13 + player.level/3.5)) #Encourage player with high AC
        return Score

    def choose_att_target(self, fight, AttackIsRanged = False, other_dmg = False, other_dmg_type = False, is_silent = False):
        player = self.player
        if other_dmg == False:
            dmg = player.dmg
        else:
            dmg = other_dmg
        if other_dmg_type == False:
            dmg_type = player.damage_type
        else:
            dmg_type = other_dmg_type
        #function returns False if no target in reach
        #this function takes all targets that are possible in reach and choosed which one is best to attack
        #the AttackIsRanged is to manually tell the function that the Attack is ranged, even if the player might not have ranged attacks, for Spells for example
        EnemiesInReach = player.enemies_reachable_sort(fight, AttackIsRanged)

        if player.dash_target != False:
            if player.dash_target.state == 1:
                #If the Dash Target from last turn is still alive, attack
                return player.dash_target

        if len(EnemiesInReach) == 0:
            if is_silent == False:
                player.DM.say('There are no Enemies in reach for ' + player.name + ' to attack', True)
                player.move_position() #if no target in range, move a line forward
                player.attack_counter = 0
            return False  #return, there is no target
        else:
            target_list = EnemiesInReach
            if self.player.strategy_level < 3:
                return target_list[int(random()*len(target_list))] #if low strategy, attack random
            #This function is the intelligence behind choosing the best target to hit from a List of given Targets. It chooses reguarding lowest Enemy and AC and so on
            ThreatScore = np.zeros(len(target_list))
            for i in range(0, len(target_list)):
                ThreatScore[i] = self.target_attack_score(fight, target_list[i], dmg_type, dmg)
            return target_list[np.argmax(ThreatScore)]

    def target_attack_score(self, fight, target, dmg_type, dmg):
        #This functions helps in decision on a att taget by assining a score
        player = self.player
        Score = 0
        RandomWeight = player.random_weight
        #random factor between 1 and the RandomWeight
        #Random Weight of 0 is no random, should not be 
        #Random Weight around 2 is average 
        
        TargetDPS = target.dps()
        PlayerDPS = player.dps()

        #Immunity
        if dmg_type in target.damage_immunity:
            return 0      #makes no sense to attack an immune target
        #Dmg done by the creature
        Score += TargetDPS*(random()*RandomWeight + 1) #Damage done per round so far
        #How Low the Enemy is
        Score += TargetDPS*(target.HP - target.CHP)/target.HP*(random()*RandomWeight + 1)
        #Heal given
        Score += target.heal_given/player.DM.rounds_number*(random()*RandomWeight + 1)

        #Target is unconscious or can be One Shot
        if player.strategy_level > 5:
            if target.state == 0: #encourage only if strategic
                Score += TargetDPS*2*(random()*RandomWeight + 1)
        elif target.CHP <= dmg: #kill is good, oneshot is better
            Score += TargetDPS*4*(random()*RandomWeight + 1)
        elif dmg > target.HP*2: #Can Instakill
            Score += TargetDPS*5*(random()*RandomWeight + 1)

        #Hit low ACs
        if (target.AC - player.tohit)/20 < 0.2:
            Score += TargetDPS*(random()*RandomWeight + 1)
        elif (target.AC - player.tohit)/20 < 0.35:
            Score += TargetDPS/2*(random()*RandomWeight + 1) #Good to hit 
        #Dont Attack high AC
        if (target.AC - player.tohit)/20 > 0.8: #90% no hit prop
            Score -= TargetDPS*(random()*RandomWeight + 1)

        if player.strategy_level > 4:
            #Attack player with your Vulnerability as dmg
            if target.last_used_DMG_Type in player.damage_vulnerability:
                Score += TargetDPS*(random()*RandomWeight + 1)
            if dmg_type in target.damage_vulnerability:
                Score += TargetDPS*(random()*RandomWeight + 1)
            elif dmg_type in target.damage_resistances:
                Score -= TargetDPS*2*(random()*RandomWeight + 1)

            #Spells
            if player.restrained:
                for x in player.TM.TokenList:
                    if x.type == 'r' and x.origin == target:
                        Score += PlayerDPS*2*(random()*RandomWeight + 1) #This player is entangling you 
            if player.is_hexing: #Check for hexing
                for HexedToken in player.CurrentHexToken.links:
                    if HexedToken.TM.player == target:
                        Score += (TargetDPS + 3.5)*(random()*RandomWeight + 1) #Youre hexing this player
            if player.is_hunters_marking: #Check for hunters Mark
                for Token in player.CurrentHuntersMarkToken.links:
                    if Token.TM.player == target:
                        Score += (TargetDPS + 3.5)*(random()*RandomWeight + 1) #Youre hexing this player

        if target.is_concentrating: Score += TargetDPS/3*(random()*RandomWeight + 1)
        if target.has_summons: Score += TargetDPS/2*(random()*RandomWeight + 1)
        if target.has_armor_of_agathys: Score -= PlayerDPS/3*(random()*RandomWeight + 1)

        if target.restrained or target.prone or target.is_blinded or target.is_stunned or target.is_paralyzed: #Attack with advantage
            Score += TargetDPS/4*(random()*RandomWeight + 1)
        if target.is_dodged: Score -= dmg/5*(random()*RandomWeight + 1)

        #Wild shape, it is less useful to attack wildshape forms
        if target.is_shape_changed and target.knows_combat_wild_shape == False:
            Score = Score*0.8*(random()*RandomWeight + 1)
        if target.shape_HP <= dmg:
            Score = Score*1.4*(random()*RandomWeight + 1)

        #this whole part took too long in performance
        # NeedDash = player.need_dash(target, fight)
        # if NeedDash == 1 and player.knows_cunning_action == False:
        #     Score -= PlayerDPS/1.3*(random()*RandomWeight + 1)
        #     #Player cant attack this turn if dashed
        # elif NeedDash == 1 and player.knows_cunning_action:
        #     Score -= dmg/2*(random()*RandomWeight + 1)
        # elif NeedDash == 1 and player.knows_eagle_totem:
        #     Score -= dmg/2*(random()*RandomWeight + 1)
        #     #With cunning action/eagle totem less of a Problem
        # if player.will_provoke_Attack(target, fight):
        #     if player.knows_eagle_totem:
        #         Score -= PlayerDPS/6*(random()*RandomWeight + 1)
        #     elif player.CHP > player.HP/3: 
        #         Score -= PlayerDPS/4*(random()*RandomWeight + 1)
        #     else: 
        #         Score -= PlayerDPS/2*(random()*RandomWeight + 1)

        #Line Score, Frontliner will go for front and mid mainly
        if player.position == 0: #front
            if target.position == 0: Score = Score*1.4
            elif target.position == 1: Score = Score*1.2
            elif target.position == 2: Score = Score*0.8
        elif player.position == 1: #Mid
            if target.position == 0: Score = Score*1.4
            elif target.position == 1: Score = Score*1.3
            elif target.position == 2: Score = Score*1.1
            elif target.position == 3: Score = Score*1.1
        elif player.position == 2: #Back
            if target.position == 2: Score = Score*1.3
            elif target.position == 3: Score = Score*1.4
        elif player.position == 3: #Airborn
            if target.position == 2: Score = Score*1.3
        
        if target.is_a_turned_undead:
            Score = Score/4 #almost no threat at the moment
        return Score

    def spell_cast_check(self, spell):
        player = self.player
        #This function checks if a given Spell is castable for the player by any means, even with quickened Spell
        #False - not castable
        #1 - castable
        #2 - only Castable via QuickenedSpell
        if spell.is_known == False:
            return False
        #Check if Player has spellslots
        if spell.spell_level > 0:
            good_slots = sum([1 for i in range(spell.spell_level - 1,9) if player.spell_slot_counter[i] > 0])
            if good_slots == 0:
                return False
        
        if player.raged:
            return False
        if player.is_in_wild_shape:
            return False
        elif spell.is_concentration_spell and player.is_concentrating:
            return False
        elif spell.is_reaction_spell:
            return False   #reaction Spell in own turn makes no sense
        elif spell.is_cantrip == False and player.has_cast_left == False:
            return False


        #Action Check
        if spell.is_bonus_action_spell and player.bonus_action == 1:
            if spell.is_cantrip:
                return 1         #have BA, is cantrip -> cast 
            elif player.has_cast_left:
                return 1        #have BA, is spell, have caste left? -> cast
            else:
                return False    #cant cast, have already casted
        elif spell.is_bonus_action_spell == False:
            if player.action == 1:
                if spell.is_cantrip:
                    return 1 #have action and is cantrip? -> cast
                elif player.has_cast_left:
                    return 1 #have action and cast left? -> cast
                else:
                    return False
            elif player.bonus_action == 1 and player.knows_quickened_spell and player.sorcery_points >= 2:
                if spell.is_cantrip:
                    return 2  #Cast only with Quickened Spell
                elif player.has_cast_left:
                    return 2  #have cast left?
                else:
                    return False
            else:
                return False
        else:
            return False

    def choose_smallest_slot(self, MinLevel, MaxLevel):
        #Returns the smallest spellslot that is still available in the range
        #MaxLevel is cast level, so MaxLevel = 4 means Level 4 Slot
        #False, no Spell Slot available
        if MaxLevel > 9: MaxLevel = 9
        if MinLevel < 1: MinLevel = 1
        for i in range(MinLevel-1, MaxLevel):
            if self.player.spell_slot_counter[i]>0:  #i = 0 -> lv1 slot
                return i+1
        return False 

    def choose_highest_slot(self, MinLevel, MaxLevel):
        #Returns the highest spellslot that is still available in the range
        #MinLevel is cast level, so MinLevel = 4 means Level 4 Slot
        #False, no Spell Slot available
        if MaxLevel > 9: MaxLevel = 9
        if MinLevel < 1: MinLevel = 1
        for i in reversed(range(MinLevel-1, MaxLevel)):
            if self.player.spell_slot_counter[i]>0:
                return i+1
        return False 

    def choose_player_to_protect(self, fight):
        #Chooses one other allies, that is not self, which might be unconsious
        player = self.player
        allies = [x for x in fight if x.team == player.team and x.state != -1 and x != player]       #which allies left alive
        if len(allies) == 0: return False #no allies

        AllyScore = []
        for ally in allies:
            AllyScore.append(self.ally_score(ally)) #get score

        #Return Ally with lowest SCore        
        return allies[np.argmin(AllyScore)]

    def ally_score(self, fight, ally):
        #The higher the score, the less likely this player needs protection
        Score = 0
        Score += ally.AC #Low AC?
        Score += ally.AC*ally.CHP/ally.HP #Low on HP?
        Score += ally.HP/10
        if ally.state == 0: Score = Score*0.5
        conditions = [
            ally.is_blinded, ally.is_stunned, ally.is_incapacitated, ally.is_paralyzed
        ]
        if any(conditions): Score*0.5
        if ally.is_shape_changed: Score = Score*3
        if ally.is_concentrating: Score = (Score- 5)/2
        Score = Score*(1 + random()*(10/self.player.strategy_level - 1)/3) #randomness from strategy
        return Score

#---------Spells
    def choose_quickened_cast(self):
        #This function is called once per trun to determine if player wants to use quickned cast this round
        player = self.player
        QuickScore = 100
        QuickScore = QuickScore*(1.5 - 0.5*(player.CHP/player.HP)) #encourage quickend cast if youre low, if CHP -> 0, Score -> 150
        if player.has_cast_left: QuickScore = QuickScore*1.4    #encourage if you havend cast yet
        if player.sorcery_points < player.sorcery_points_base/2: QuickScore = QuickScore*0.9 #disencourage for low SP
        elif player.sorcery_points < player.sorcery_points_base/3: QuickScore = QuickScore*0.8
        elif player.sorcery_points < player.sorcery_points_base/5: QuickScore = QuickScore*0.7
        if player.restrained: QuickScore = QuickScore*1.1  #Do something against restrained
        #Random Power for quickened Spell
        QuickScore = QuickScore*(0.65 + random()*0.7) #+/- 35%
        if QuickScore > 100:
            return True
        else:
            return False

    def choose_spell(self, fight):
        #This function chooses a spell for the spell choice
        #If this function return False, spellcasting is not an option for this choice
        player = self.player
        SpellChoice = False

        #Check the absolute Basics
        if player.action == 0 and player.bonus_action == 0:
            return False, 0
        if player.raged == 1:
            return False, 0   #cant cast while raging

        Choices = []

        #Check Spells
        for x, spell in player.SpellBook.items():
            Checkvalue = self.spell_cast_check(spell) #check if castable
            if Checkvalue == 1: #Check, Spell is castable
                Choices.append(spell.cast)
                #Check if Twin cast is an option
            if all([Checkvalue == 1, spell.is_twin_castable, player.knows_twinned_spell, player.sorcery_points > spell.spell_level, player.sorcery_points > 1]):
                Choices.append(spell.twin_cast)
            elif Checkvalue == 2: #Spell is only castable via quickened spell
                Choices.append(spell.quickened_cast)

        #This function determines if the player wants to cast a quickened spell this round
        if player.knows_quickened_spell:
            cast_quickened_this_round = self.choose_quickened_cast()
        else:
            cast_quickened_this_round = False

        ChoiceScores = [0 for i in Choices]
        if len(Choices) == 0:
            return False, 0  #if no spell is castable return False
        TargetList = [[player] for i in Choices] #will be filled with targets
        LevelList = [0 for i in Choices]#at what Level the Spell is casted
        for i in range(0, len(Choices)):
            Choice = Choices[i]
            Score = 0

        #In the following all Options will get a score, that roughly resembles their dmg or equal dmg value
        #This Score is assigned by a function of the spellcasting class 
        #This function also evalues if it is good to use a quickened or twin cast
        #The evaluation of quickened Cast is currently not handled by these functions
            for x, spell in player.SpellBook.items():
                if Choice == spell.cast:
                    Score, SpellTargets, CastLevel = spell.score(fight)
                elif Choice == spell.quickened_cast:
                    if cast_quickened_this_round == True:
                        Score, SpellTargets, CastLevel = spell.score(fight)
                    else:
                        #Basically dont cast quickened this round
                        Score = 0
                        SpellTargets = [player]
                        CastLevel = 0
                elif Choice == spell.twin_cast:
                    Score, SpellTargets, CastLevel = spell.score(fight, twinned_cast=True)
            ChoiceScores[i] = Score
            TargetList[i] = SpellTargets
            LevelList[i] = CastLevel
        #Now find best value and cast that
        ChoiceIndex = np.argmax(ChoiceScores)

        #Before returning the Value check if it is even sensable to cast instaed of doing something else
        #This part gives a Value of the possible alternatives and assignes a dmg equal value to compare with
        #This is the Score that will be compared for the action Spell, so assume an action is left
        if player.action == 1:
            #If the player has still its action, compete with this alternative score of just attacking
            if np.max(ChoiceScores) > player.dmg/4:
                SpellChoice = partial(Choices[ChoiceIndex],TargetList[ChoiceIndex],LevelList[ChoiceIndex])
                return SpellChoice, ChoiceScores[ChoiceIndex]
            else:
                return False, 0 #If you have action and cant beat this Score, dont cast spell
        elif player.bonus_action == 1:
            if np.max(ChoiceScores) > player.dmg/5 + 1:    #just a small threshold
                    SpellChoice = partial(Choices[ChoiceIndex],TargetList[ChoiceIndex],LevelList[ChoiceIndex])
                    return SpellChoice, ChoiceScores[ChoiceIndex]
            else:
                return False, 0
        else: return False, 0

    def choose_heal_target(self, fight):
        #This function is called if the player has heal
        #It returns the best Target for a heal and gives the Heal a Score
        #If False is returned, Heal will not be added as a Choice for this turn
        player = self.player
        if self.dying_allies != []:      #someone is dying
            DyingScore = []
            for ally in self.dying_allies:
                Score = ally.dps()*ally.death_counter #High Score for a high death_counter
                Score += ally.value()
                Score = Score*0.7*(0.8+random()*0.4) #little random power
                #The Score will be returned as a Score for the Choices in do_your_turn too
                DyingScore.append(Score)
            MaxIndex = np.argmax(DyingScore)
            Target = self.dying_allies[MaxIndex]
            return Target, DyingScore[MaxIndex]
        #No One is currently dying
        else:
            TeamHP = sum([x.HP for x in self.allies])
            TeamCHP = sum([x.CHP for x in self.allies])
            if TeamCHP/TeamHP < 0.7:
                HealScores = []
                for ally in self.allies:
                    Score = ally.value()*2/3 #Player is not dead, might still do another round
                    Score = Score*(1 - ally.CHP/ally.HP) #Score Scales with CHP left
                    Score = Score*(0.8+random()*0.4)
                    if ally.CHP/ally.HP > 0.6:
                        Score = 0
                    HealScores.append(Score)
                MaxIndex = np.argmax(HealScores)
                if HealScores[MaxIndex] > player.value()/3: #Minimum Boundry for reasonable heal
                    return self.allies[MaxIndex], HealScores[MaxIndex]
                else:
                    return False, 0
            else:
                return False, 0

    def choose_heal_spellslot(self, MinLevel = 1):
        player = self.player
        SpellPower = sum([player.spell_slot_counter[i]*np.sqrt((i + 1)) for i in range(0,9)])
        MaxSlot = 0 # Which is the max spell slot left
        for i in reversed(range(0,9)):
            if player.spell_slot_counter[i] > 0:
                MaxSlot = i + 1
                break

        TestLevel = int(SpellPower/5 + 1.5)
        if TestLevel == MaxSlot:
            #Never use best slot to heal
            TestLevel -= 1
        
        #Use the TestLevel Slot or the next best lower then it
        LowLevel = self.choose_highest_slot(1,TestLevel)
        if LowLevel != False:
            return LowLevel
        #if no low level left, try higher
        HighLevel = self.choose_smallest_slot(TestLevel+1,9)
        if HighLevel != False:
            return HighLevel
        return False

    def choose_new_hex(self, fight):
        HexChoices = [x for x in fight if x.team != self.player.team and x.state == 1]
        HexTarget = self.choose_att_target(HexChoices, AttackIsRanged=True, other_dmg=3.5, is_silent=True)
        if HexTarget != False and self.player.bonus_action == 1:
            self.player.SpellBook['Hex'].change_hex(HexTarget)

    def choose_new_hunters_mark(self, fight):
        HuntersMarkChoices = [x for x in fight if x.team != self.player.team and x.state == 1]
        Target = self.choose_att_target(HuntersMarkChoices, AttackIsRanged=True, other_dmg=3.5, is_silent=True)
        if Target != False:
            self.player.SpellBook['HuntersMark'].change_hunters_mark(Target)

#Tools
class dmg:
    def __init__(self, amount = 0, type = 'slashing'):
        #List with float dmg amounts
        self.dmg_amount_list = []
        #List with dmg_type strings
        self.dmg_type_list = []
        self.types = ['acid', 'cold', 'fire', 'force' , 'lightning',
        'thunder', 'necrotic', 'poison', 'psychic' ,'radiant', 
        'bludgeoning', 'piercing', 'slashing', 'true', 'heal']
        self.DMGSubstract = 0
        #If a first dmg is passed:
        if amount != 0:
            self.add(amount, type)
    
    def add(self, amount, type):
        for x in self.types:
            if x in type:
                #Check if maybe alredy in
                for i in range(0,len(self.dmg_type_list)):
                    if x == self.dmg_type_list[i]:
                        self.dmg_amount_list[i] += amount
                        return
                #else
                self.dmg_amount_list.append(amount)
                self.dmg_type_list.append(x)
                return
        print('Unknown Dmg Type: ' + type)
        quit()

    def multiply(self, factor):
        #All dmg entries are multiplied
        self.dmg_amount_list = [x*factor for x in self.dmg_amount_list]

    def substract(self, amount):
        #should be positive
        self.DMGSubstract += amount

    def abs_amount(self):
        return sum(self.dmg_amount_list) - self.DMGSubstract
    
    def calculate_for(self, player):
            DMGTotal = 0
            for i in range(0, len(self.dmg_amount_list)):
                DMGType  = self.dmg_type_list[i]
                if DMGType in player.damage_resistances or DMGType in player.additional_resistances:
                    player.DM.say(str(player.name) + ' is resistant against ' + DMGType, True)
                    self.dmg_amount_list[i] = self.dmg_amount_list[i]/2
                    DMGTotal += self.dmg_amount_list[i]
                elif DMGType in player.damage_immunity:
                    player.DM.say(str(player.name) + ' is immune against ' + DMGType, True)
                    self.dmg_amount_list[i] = 0
                    DMGTotal += 0
                elif DMGType in player.damage_vulnerability:
                    player.DM.say(str(player.name) + ' is vulnarable against ' + DMGType, True)
                    self.dmg_amount_list[i] = self.dmg_amount_list[i]*2
                    DMGTotal += self.dmg_amount_list[i]
                else:
                    DMGTotal += self.dmg_amount_list[i]
            if DMGTotal < 0: return DMGTotal  #It is heal, so return, do not substract from heal

            #If dmg was substracted from this amount, do it now, if < 0, do not heal
            if self.DMGSubstract > DMGTotal: return 0
            else:
                DMGTotal -= self.DMGSubstract
                return DMGTotal
        
    def damage_type(self):
        #Return type of first
        return self.dmg_type_list[0]
    
    def text(self):
        string = ''
        for i in range(0,len(self.dmg_amount_list)):
            if self.dmg_amount_list[i] != 0:
                string += str(round(self.dmg_amount_list[i],2))
                string += ' ' + self.dmg_type_list[i] + ' '
        if self.DMGSubstract > 0:
            string += ' - ' + str(round(self.DMGSubstract,2))  #substracted
        return string

    def print(self):
        print(self.dmg_amount_list)
        print(self.dmg_type_list)        

class ifstatements:
    def __init__(self, rules, errors, DM):
        self.rules = rules
        self.errors = errors
        self.DM = DM
    
    def check(self):
        if all(self.rules):
            return
        else:
            for i in range(0,len(self.rules)):
                if self.rules[i] == False:
                    print(self.errors[i])
                    quit()

#Tokens

class TokenManager():
    #This Class handles all the Tokens a player might have
    #The Tokens realate Player with each other and and checks for state changes
    #If a Token is added, the Token Manager updates possible changes

    def __init__(self, player):
        self.player = player

        if self.player.DM.AI_blank: #this is only a dirty trick so that VScode shows me the attributes of player and MUST be deactived
            self.player = entity('test', 0, 0)
        self.TokenList = []

        #This dict contains all the subtypes and
        #what attribute of the player they set to True
        #if such a Token is in the TM
        self.subtype_dict = {'r' : ['restrained'],
                            'bl' : ['is_blinded'],
                            'st' : ['is_stunned', 'is_incapacitated'],
                            'pl' : ['is_paralyzed', 'is_incapacitated'],
                            'ps' : ['is_poisoned'],
                            'iv' : ['is_invisible'],
                            'h' : ['is_hasted'],
                            'hex' : ['is_hexed'],
                            'hexn' : ['is_hexing'],
                            'hm' : ['is_hunters_marked'],
                            'hmg' : ['is_hunters_marking'],
                            'ck' : ['is_cloud_killing'],
                            'sr' : ['is_using_sickening_radiance']
                            }
    
    def add(self, Token):
        self.TokenList.append(Token)
        self.update()
    
    def resolve(self, Token):
        if Token in self.TokenList:
            self.TokenList.remove(Token)
        self.update()
    
    def resolveAll(self):
        while len(self.TokenList) > 0:
            self.TokenList[0].resolve()

    def listAll(self):
        for x in self.TokenList:
            x.identify()
    
    def update(self):
        player = self.player
        #This is important for effects that could come from multiple sources
        #That is why this can not be handled via the tokens, because they would not know, if the effect come from more then one token
        #Concentration on the other hand is handled via the con token class

        #Got a new Token, Update Player Stats, like Concentration
        #First all attributes are set to false
        #Then all tokens are looped and if they have a key the corresponding attribute is set to true
        #Conditions
        player.restrained = False
        player.is_stunned = False
        player.is_incapacitated = False
        player.is_paralyzed = False
        player.is_blinded = False
        player.is_poisoned = False
        player.is_invisible = False

        player.is_hasted = False #preset to false
        player.is_hexed = False
        player.is_hexing = False
        player.is_hunters_marked = False
        player.is_hunters_marking = False
        player.is_cloud_killing = False
        player.is_using_sickening_radiance = False


        for x in self.TokenList: #Loop the List of all Tokens
            for key in list(self.subtype_dict.keys()): #Loop the List of Subtype keys for each token
                if x.subtype == key: #If the subtype of that token is the key
                    for player_att in self.subtype_dict[key]: #Set all the corresponding Attributes to true
                        setattr(player, player_att, True)
        
    def checkFor(self, subtype):
        #This Function tests for a Subtype String tag
        #Returns Boolean
        for x in self.TokenList:
            if x.subtype == subtype: return True
        return False

#-----------Resolve and Trigger Conditions
    def break_concentration(self):
        for x in self.TokenList:
            if x.type == 'con': #break concentration
                x.resolve()
                return

    def unconscious(self):
        for x in self.TokenList:
            if x.resolveWhenUnconcious: x.resolve()
            if x.triggersWhenUnconscious: x.getUnconsciousTrigger()

    def endOfTurn(self):
        #This Function is called at the end of entities Turn and resolves timers
        for x in self.TokenList:
            #Timer
            if x.hasATimer:
                x.timer -= 1  #another Round is over
                if x.timer < 1: #Timer is over
                    x.resolve() #Timer based Token is resolved
            #End of Turn
            if x.resolveAtTurnEnd: x.resolve()
            if x.triggersWhenEndOfTurn: x.endOfTurnTrigger()

    def startOfTurn(self):
        #Attention, is called in entity class and this is calles in do_the_fighting
        #ONLY called if player.state == 1
        for x in self.TokenList:
            if x.resolveAtTurnStart: x.resolve()
            if x.triggersWhenStartOfTurn: x.startOfTurnTrigger()

    def hasHitWithAttack(self, target, Dmg, is_ranged, is_spell):
        #This function triggers all Tokens with the Trigger
        #Is called from the attack function if player hit with an attack
        for x in self.TokenList:
            if x.triggersWhenAttackHasHits: x.hasHitWithAttackTrigger(target, Dmg, is_ranged, is_spell)

    def washitWithAttack(self, attacker, Dmg, is_ranged, is_spell):
        #This function triggers all Tokens with the Trigger
        #Is called from the attack function of player was hit with an attack
        for x in self.TokenList:
            if x.triggersWhenHitWithAttack: x.wasHitWithAttackTrigger(attacker, Dmg, is_ranged, is_spell)

    def death(self):
        for x in self.TokenList:
            if x.resolveWhenUnconcious or x.resolveWhenDead:
                x.resolve()
            if x.triggersWhenUnconscious: x.getUnconsciousTrigger()

    def isAttacked(self, attacker, is_ranged, is_spell):
        for x in self.TokenList:
            if x.triggersWhenAttacked: x.wasAttackedTrigger(attacker, is_ranged, is_spell)

    def hasDroppedShape(self):
        #called in drop_shape Entity function
        for x in self.TokenList:
            if x.triggersWhenShapeIsDropped: x.dropShapeTrigger()

class Token():
    def __init__(self, TM):
        self.TM = TM
        #Only Initiate these Vars if they are not already given by a subclass:
        if hasattr(self, 'type') == False:
            self.type = ''
        if hasattr(self, 'subtype') == False:
            self.subtype = ''
        self.resolveWhenUnconcious = False
        self.resolveWhenDead = False
        self.resolveAtTurnStart = False
        self.resolveAtTurnEnd = False
        self.hasATimer = False
        self.timer = 0

        self.triggersWhenAttackHasHits = False
        self.triggersWhenHitWithAttack = False
        self.triggersWhenUnconscious = False
        self.triggersWhenEndOfTurn = False
        self.triggersWhenStartOfTurn = False
        self.triggersWhenAttacked = False
        self.triggersWhenShapeIsDropped = False

        self.TM.add(self) #add and update the Token to TM
    
    def resolve(self):
        #Is the Way to resolve a Token
        #Is then removed from TM list
        #Should be run last
        self.TM.resolve(self)

    def wasAttackedTrigger(self, attacker, is_ranged, is_spell):
        #This is a function of a Token
        #It is called if the Character at start of beeing attacked, before hit or miss check
        #It is a function, that not automatically resolves the token
        return

    def wasHitWithAttackTrigger(self, attacker, Dmg, is_ranged, is_spell):
        #This is a function of a Token
        #It is called if the Character was hit with an attack
        #It is a function, that not automatically resolves the token
        return

    def hasHitWithAttackTrigger(self, target, Dmg, is_ranged, is_spell):
        #This is a function of a Token
        #It is called if the Character has hit with an attack
        #It is a function, that not automatically resolves the token
        return 

    def getUnconsciousTrigger(self):
        #this function is called if the target gets unconscious and has teh trigger
        return

    def endOfTurnTrigger(self):
        return

    def startOfTurnTrigger(self):
        return

    def dropShapeTrigger(self):
        return

    def identify(self):
        print(str(self))

class LinkToken(Token):
    #This is a token to give as a Token for a effect of any kind that is linked to another Token
    #Link Tokens have an origin
    #If the resolve, they unlink from origin
    def __init__(self, TM, subtype):
        self.subtype = subtype
        self.type = 'l' #Concentration Link
        super().__init__(TM)
        self.origin = False  #Will be linked by the Origin Token

    def resolve(self):
        self.origin.unlink(self) #unlink from Origin
        return super().resolve()

class DockToken(Token):
    #this Kind of Token can accept Link Tokens
    #It will resolve
    #It Accepts a List of Links
    def __init__(self, TM, links):
        super().__init__(TM)

        if type(links) != list: self.links = [links]
        else: self.links = links

        #Now link this Spell as origin to thier links
        for x in self.links:
            x.origin = self
        #Any Lined Tokens will be resolved if Dock token is resolved

    def addLink(self, Token):
        #Add a Link and set this Dock as origin
        self.links.append(Token)
        Token.origin = self

    def resolve(self):
        #If you resolve Dock Token, resolve all links to this Token
        while len(self.links) > 0:
            self.links[0].resolve()#resolve all
        super().resolve()

    def unlink(self, CLToken):
        #This function takes a Link Token out of the link list
        self.links.remove(CLToken)
        CLToken.origin = False #No origin anymore
        #Check if this was last link
        if len(self.links) == 0:
            self.resolve() #resolve if no links left

class ConcentrationToken(DockToken):
    #This is a token to give to a player when concentrating
    def __init__(self, TM, links):
        #is a Dock Token, all linked Tokens are resolved, if this Token is resolved
        self.type = 'con'

        #Check for concentration before initiating
        if TM.player.is_concentrating:
            print(TM.player.name + ' tried to initiate concentration while concentrated')
            quit()
        TM.player.is_concentrating = True #set concentration

        super().__init__(TM, links)

    def resolve(self):
        super().resolve()
        #After the super().resolve from the dock token all link token are resolved aswell
        if self.TM.player.is_concentrating:
            #The if statement is here, because, the resolve function might be called twice
            #If the dock token is resolved, it resolves all links, which in turn resolve the dock token
            self.TM.player.is_concentrating = False #No longer concentrated
            self.TM.player.DM.say(self.TM.player.name + ' no longer concentrated')

#-------------Spell Tokens----------
class EntangledToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenUnconcious = True
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' breaks Entangle, ', True)
        return super().resolve()

class HastedToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.hasATimer = True
        self.resolveWhenDead = True
        self.resolveWhenUnconcious = True
        self.timer = 10 #10 Rounds
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' Haste wares of, ', True)
        LostHaseToken(self.TM)
        #This Token will resolve at start of players Turn
        #Will take away action and bonus action
        return super().resolve()

class LostHaseToken(Token):
    #Give this Token to a player that just lost haste
    def __init__(self, TM):
        super().__init__(TM)
        self.resolveAtTurnStart = True
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' is tiered from Haste', True)
        self.TM.player.action = 0
        self.TM.player.attack_counter = 0
        self.TM.player.bonus_action = 0
        return super().resolve()

class HexedToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenUnconcious = True
        self.triggersWhenHitWithAttack = True #add hex dmg

    def wasHitWithAttackTrigger(self, attacker, Dmg, is_ranged, is_spell):
        if attacker.TM == self.origin.TM: #Attacker is hexing you
            Dmg.add(3.5, 'necrotic')
            self.TM.player.DM.say(self.TM.player.name + ' was cursed with a hex: ', True)
            return

    def resolve(self):
        self.TM.player.DM.say(', hex of ' + self.TM.player.name + ' is unbound ')
        if self.origin.TM.player.CurrentHexToken != False:
            #Only set new hex, is orgin still concentrated on hex
            self.origin.TM.player.can_choose_new_hex = True
        super().resolve()

class HexingToken(ConcentrationToken):
    def __init__(self, TM, links):
        self.subtype = 'hexn' #Is hexing token
        super().__init__(TM, links)
    
    def unlink(self, CLToken):
        #This function takes a Concentration Link Token out of the link list
        self.links.remove(CLToken)
        #Usually a Concentration Token is resolved if all links are unlinked
        #But Hex can switch Tokens multiple times
        #The Spell Function creates a new link, the old link is unlinked but the Hex Token not resolved

    def resolve(self):
        #If concentration breaks, before plyer choose a new hex, then can_choose_new_hex might still be True
        self.TM.player.can_choose_new_hex = False
        self.TM.player.CurrentHexToken = False
        self.TM.player.is_hexing = False
        return super().resolve()

class HuntersMarkedToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenUnconcious = True
        self.triggersWhenHitWithAttack = True #add HM dmg

    def wasHitWithAttackTrigger(self, attacker, Dmg, is_ranged, is_spell):
        if attacker.TM == self.origin.TM and is_spell == False: #Attacker is hexing you
            Dmg.add(3.5, self.origin.TM.player.damage_type)
            self.TM.player.DM.say(self.TM.player.name + ' was hunters marked: ', True)
            return

    def resolve(self):
        self.TM.player.DM.say(', hunters mark of ' + self.TM.player.name + ' is unbound ')
        if self.origin.TM.player.CurrentHuntersMarkToken != False:
            #Only set new hunters Mark, if orgin still concentrated on HM
            self.origin.TM.player.can_choose_new_hunters_mark = True
        super().resolve()

class HuntersMarkingToken(ConcentrationToken):
    def __init__(self, TM, links):
        self.subtype = 'hmg' #Is hunters marking token
        super().__init__(TM, links)
    
    def unlink(self, CLToken):
        #This function takes a Concentration Link Token out of the link list
        self.links.remove(CLToken)
        #Usually a Concentration Token is resolved if all links are unlinked
        #But hunters mark can switch Tokens multiple times
        #The Spell Function creates a new link, the old link is unlinked but the hunters mark Token not resolved

    def resolve(self):
        #If concentration breaks, before plyer choose a new hunters mark, then can_choose_new_hunters_mark might still be True
        self.TM.player.can_choose_new_hunters_mark = False
        self.TM.player.CurrentHuntersMarkToken = False
        return super().resolve()

class GuidingBoltedToken(LinkToken):
    #Is a Link Token, will unlink if resolved, then the GuidingBolt Token will also resolved
    def __init__(self, TM):
        subtype = 'gb'
        super().__init__(TM, subtype)
        self.triggersWhenAttacked = True  #Guiding Bolt gives Advantage if attacked

    def wasAttackedTrigger(self, attacker, is_ranged, is_spell):
        self.TM.player.is_guiding_bolted = True
        #This is reset in the make_attack_roll function
        return super().resolve()

class GuidingBoltToken(DockToken):
    #Is a Dock Token with a Timer, if resolved will also resolve the Linked Token
    def __init__(self, TM, links):
        super().__init__(TM, links)
        self.hasATimer = True
        self.timer = 2        #Till End of next Turn

class SummonerToken(ConcentrationToken):
    def __init__(self, TM, links):
        TM.player.has_summons = True #is now summoning
        super().__init__(TM, links)
    
    def resolve(self):
        self.TM.player.has_summons = False
        return super().resolve()
    
class SummenedToken(LinkToken):
    #This Sumclass is a token to give a summoned Creature
    #It will Vanish after it dies
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenDead = True
        self.resolveWhenUnconcious = True
        self.TM.player.is_summoned = True #Will be removed from fight if dead
    
    def resolve(self):
        summon = self.TM.player
        if summon.is_summoned == False:
            print('This is not a summon')
            quit()
        if summon.summoner == False:
            print('Should have a summoner')
            quit()
        
        summon.DM.say(summon.name + ' vanishes ', True)
        summon.CHP = 0
        summon.state = -1
        return super().resolve()

class WallOfFireProtectedToken(LinkToken):
    def __init__(self, TM, subtype, damage):
        super().__init__(TM, subtype)
        self.damage = damage
        self.triggersWhenAttacked = True #protect one player from attacks
        self.last_target = None #Will not trigger on same player in a row
        self.hit_counter = 3 #will only trigger 3 times

    def wasAttackedTrigger(self, attacker, is_ranged, is_spell):
        #The protected player was attacked
        #Only trigger a limited number of times
        if self.hit_counter < 1: return
        #check if it was the same attacker as last time
        if attacker == self.last_target: return
        #dmg the attacker
        self.TM.player.DM.say(attacker.name + ' must go trough the wall of fire ', True)
        dmg_to_apply = dmg(self.damage, 'fire')
        original_caster = self.origin.TM.player #caster of wall of fire
        attacker.last_attacker = original_caster
        #apply dmg to the attacker
        attacker.changeCHP(dmg_to_apply, original_caster, True)

        #Now handle the walls own logic:
        #Remember the last hit target, that went in the wall
        self.last_target = attacker
        #lower the hit counter by one
        self.hit_counter -= 1
        if self.hit_counter < 1:
            #Wall got useless
            self.TM.player.DM.say(self.TM.player.name + 's wall of fire got strategically useless and was dropped, ', True)
            self.resolve()
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + 's wall of fire vanishes ')
        return super().resolve()

class CloudkillToken(ConcentrationToken):
    #Is Concentration Token, lets the caster recast spell
    def __init__(self, TM, links, castLevel):
        self.subtype = 'ck' #cloud kill (sets the self.is_cloud_killing = True)
        super().__init__(TM, links)
        self.castLevel = castLevel

    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + 's cloudkill vanishes ')
        super().resolve()

class SickeningRadianceToken(ConcentrationToken):
    #Is Concentration Token, lets the caster recast spell
    def __init__(self, TM, links, castLevel):
        self.subtype = 'sr' #sickening radiance (sets the self.is_using_sickening_radiance = True)
        super().__init__(TM, links)
        self.castLevel = castLevel
    
    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + 's sickening radiance vanishes ')
        super().resolve()

class PolymorphedToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.triggersWhenShapeIsDropped = True #To resolve when shape drops
        #It does not handle the reshaping if drop to 0, because this is handled for all alternate shapes in ChangeCHP function of entity

    def dropShapeTrigger(self):
        super().dropShapeTrigger()
        #Shape was dropped, now resolve Token
        self.resolve()

    def resolve(self):
        if self.TM.player.is_shape_changed: #only drop shape if still shape changed
            self.TM.player.drop_shape() #this drops the polymorph shape
            self.TM.player.DM.say(self.TM.player.name + ' no longer polymorphed ', True)
        if self.origin != False:
            super().resolve()

class CallLightningToken(ConcentrationToken):
    #Is Concentration Token, lets the caster recast spell
    def __init__(self, TM, links, castLevel):
        self.subtype = 'cl' #cloud kill (sets the self.is_cloud_killing = True)
        super().__init__(TM, links)
        self.castLevel = castLevel
        playerAI = self.TM.player.AI
        #Add the call lightning choice to player AI
        playerAI.add_choice(playerAI.callLightningChoice)

    def resolve(self):
        playerAI = self.TM.player.AI
        #When this token resolves it removes the call lightning choice from Choices again
        playerAI.remove_choice(playerAI.callLightningChoice)
        self.TM.player.DM.say(self.TM.player.name + 's called lightning vanishes ')
        super().resolve()

#--------------Other Ability Tokens-----------------
class EmittingProtectionAuraToken(DockToken):
    def __init__(self, TM, links):
        super().__init__(TM, links)
        self.resolveWhenUnconcious = True
        self.resolveAtTurnStart = True
        #every Round other protected

class ProtectionAuraToken(LinkToken):
    def __init__(self, TM, auraBonus):
        subtype = 'aop'  #aura of protection
        super().__init__(TM, subtype)
        self.auraBonus = auraBonus #Wisdom Mod of origin player
        if self.auraBonus < 1: self.auraBonus = 1

class PrimalBeastMasterToken(DockToken):
    def __init__(self, TM, links):
        #This is a Dock Token, it will resolve all links if resolved
        #It resolves if the link is resolved
        super().__init__(TM, links)
        self.resolveWhenDead = True
    
    def resolve(self):
        return super().resolve()

class PrimalCompanionToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenDead = True
        self.TM.player.is_summoned = True
    
    def resolve(self):
        summon = self.TM.player
        summon.DM.say(summon.name + ' vanishes ', True)
        summon.CHP = 0
        summon.state = -1

        return super().resolve()

class DodgeToken(Token):
    def __init__(self, TM):
        super().__init__(TM)
        self.resolveAtTurnStart = True
        self.resolveWhenDead = True
        self.resolveWhenUnconcious = True
        self.TM.player.is_dodged = True
    
    def resolve(self):
        self.TM.player.is_dodged = False
        return super().resolve()

class GreatWeaponToken(DockToken):
    def __init__(self, TM, links):
        super().__init__(TM, links)
        self.subtype = 'gw'
        self.resolveAtTurnEnd = True #after this turn, all tokens that were given for attacks are resolved
        self.resolveWhenUnconcious = True #maybe unconcious before end of turn

class GreatWeaponAttackToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.subtype = 'gwa'
        self.triggersWhenUnconscious = True #if you are hit by an attack from a great weapon master, and go unconscious, this tokens triggers
        #it also resolves at the end of the origins turn

    def getUnconsciousTrigger(self):
        #This function is called if a player is reduced to 0 HP or lower and has a great weapon attack token
        #This means it was attacked by a great weapon master in this turn
        if self.origin.TM.player.bonus_action == 1:
            self.origin.TM.player.attack_counter += 1 #player gets another attack
            self.origin.TM.player.bonus_action = 0
            self.TM.player.DM.say(', ' + self.origin.TM.player.name + ' gains extra attack')

class FavFoeMarkToken(LinkToken):
    def __init__(self, TM, subtype):
        super().__init__(TM, subtype)
        self.resolveWhenUnconcious = True
        self.triggersWhenHitWithAttack = True #add hex dmg
        self.triggersWhenEndOfTurn = True #regain one use at end of turn
        self.has_triggered_this_round = False

    def wasHitWithAttackTrigger(self, attacker, Dmg, is_ranged, is_spell):
        if self.has_triggered_this_round == False: #no double hit
            if attacker.TM == self.origin.TM: #Attacker is hexing you
                Dmg.add(self.origin.TM.player.favored_foe_dmg, self.origin.TM.player.damage_type)
                self.has_triggered_this_round = True
                self.TM.player.DM.say(self.TM.player.name + ' was marked as favored foe: ', True)
                return

    def endOfTurnTrigger(self):
        self.has_triggered_this_round = False

    def resolve(self):
        self.TM.player.DM.say(', favored foe mark of ' + self.TM.player.name + ' is unbound ')
        super().resolve()

class FavFoeToken(ConcentrationToken):
    def __init__(self, TM, links):
        self.subtype = 'fav' #Is hexing token
        super().__init__(TM, links)
        self.TM.player.has_favored_foe = True
    
    def resolve(self):
        self.TM.player.is_hexing = False
        self.TM.player.has_favored_foe = False
        return super().resolve()

class StunningStrikedToken(LinkToken): #give this to target, Dock token will be done automatically
    def __init__(self, TM):
        super().__init__(TM, "st")
        self.resolveWhenUnconcious = True

    def resolve(self):
        self.TM.player.DM.say(self.TM.player.name + ' is no longer Stunned, ', True)
        return super().resolve()

class StunningStrikeActive(DockToken):
    # Is a Dock Token with a Timer, if resolved will also resolve the Linked Token
    def __init__(self, TM, links):
        super().__init__(TM, links)
        self.hasATimer = True
        self.timer = 2  # Till End of next Turn


#Spells

class spell:
    def __init__(self, player):
        #this class is initiated at the entity for spellcasting
        self.DM = player.DM
        self.player = player            #the Player that is related to this spell Object and which will cast this spell
        self.TM = self.player.TM       #Token Manager of player 
        if self.player.DM.AI_blank: #this is only a dirty trick so that VScode shows me the attributes of player and MUST be deactived, AI_blank should be false
            self.player = entity('test', 0, 0)


        #Initial
        if hasattr(self, 'spell_name') == False:
            self.spell_name = 'undefined'          #Give Name, if not specified in subclass
        if hasattr(self, 'spell_text') == False:
            self.spell_text = 'undefined'         #This is the text name that will be printed

        self.spell_level = 0
        self.cast_level = 0 #Will be set before every cast
        self.spell_save_type = False        #Type of the Spell Save 
        self.is_bonus_action_spell = False
        self.is_concentration_spell = False
        self.is_reaction_spell = False
        self.is_cantrip = False
        self.is_twin_castable = False      #Meta Magic Option
        self.is_range_spell = False

        #Activate the Spell, if the player knows it
        self.is_known = False
        if self.spell_name in player.spell_list:
            self.is_known = True

        self.was_cast = 0

    #any spell has a specific Spell cast function that does what the spell is supposed to do
    #This Function is the cast function and will be overwritten in the subclasses
    #To do so, the make_spell_check function makes sure, that everything is in order for the self.player to cast the spell
    #The make_action_check function checks if Action, Bonus Action is used
    #the spell class objects will be linked to the player casting it by self.player

    def cast(self, targets, cast_level = False, twinned = False):
        if cast_level == False: cast_level = self.spell_level
        self.autorize_cast(cast_level)
        self.announce_cast()

    def autorize_cast(self, cast_level):
        #Checks if cast is autorized
        #Make a check if cast is possible
        if cast_level == False:
            cast_level = self.spell_level #cast as level if nothing else

        if self.is_cantrip:
            if self.make_cantrip_check() == False:
                return
        else:
            if self.make_spell_check(cast_level=cast_level) == False:
                return
        
        #If everything is autorized, set cast_level
        self.cast_level = cast_level
        self.was_cast += 1  #for spell recap

    def announce_cast(self):
        text = ''.join([self.player.name,' casts ',self.spell_text,' at lv.', str(self.cast_level)])
        self.player.DM.say(text, True)

    def score(self, fight, twinned_cast = False):
        #The Score function is called in the Choices Class
        #It is supposed to return a dmg equal score
        #It also returns the choosen SpellTargts and the CastLevel
        #If this spell is not soposed to be considered as an option this turn, return 0 score
        #This function should be overwritten in the subclassses
        return self.return_0_score()

    def make_spell_check(self, cast_level):
        #This function also sets the action, reaction or bonus action ans spell counter down
        rules = [self.is_known, 
                self.player.raged == 0,
                cast_level >= self.spell_level, 
                self.player.spell_slot_counter[cast_level -1] > 0,
                self.player.is_shape_changed == False,
                self.is_concentration_spell == False or self.player.is_concentrating==False]
        errors = [self.player.name + ' tried to cast ' + self.spell_name + ', without knowing the spell',
                self.player.name + ' tried to cast ' + self.spell_name + ' but is raging',
                self.player.name + ' tried to cast ' + self.spell_name + ' at a lower level: ' + str(cast_level),
                self.player.name + ' tried to cast ' + self.spell_name +', but spell slots level ' + str(cast_level) + ' are empty',
                self.player.name + ' tried to cast ' + self.spell_name + ', but is in wild shape',
                self.player.name + ' tried to cast ' + self.spell_name + ', but is currently concentrating']
        ifstatements(rules, errors, self.DM).check()

        #Is reaction Spell break here
        if self.is_reaction_spell:
            if self.player.reaction == 0:
                print(self.player.name + ' tired to cast ' + self.spell_name + ', but hast no reaction')
                quit()
            else:
                self.player.reaction = 0
                self.player.spell_slot_counter[cast_level-1] -= 1   #one SpellSlot used
                return True
        #check if player has cast this round
        elif self.player.has_cast_left == False:
            print(self.player.name + ' tried to cast ' + self.spell_name + ', but has already cast a spell')
            quit()
        #check is player has action/bonus action left
        elif self.make_action_check() == False:
            quit()
        #everything clear for cast
        else:
            self.player.spell_slot_counter[cast_level-1] -= 1   #one SpellSlot used
            return True

    def make_cantrip_check(self):
        rules = [self.is_known,
                self.player.raged == 0,
                self.player.is_shape_changed == False,
                self.is_concentration_spell == False or self.player.is_concentrating==False]
        errors = [self.player.name + ' tried to cast ' + self.spell_name + ', without knowing the spell',
                self.player.name + ' tried to cast ' + self.spell_name + ' but is raging',
                self.player.name + ' tried to cast ' + self.spell_name + ', but is in wild shape',
                self.player.name + ' tried to cast ' + self.spell_name + ', but is currently concentrating']
        ifstatements(rules, errors, self.DM).check()
        #check is player has action/bonus action left
        if self.make_action_check() == False:
            quit()
        #everything clear for cast
        else:
            return True        

    def make_action_check(self):
        #This function checks is the player has the required action left and sets it off if so
        #Bonus Action Spell
        if self.is_bonus_action_spell:
            #Bonus Action used?
            if self.player.bonus_action == 0:
                self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but has no Bonus Action left')
                quit()
            #Allow cast and use bonus_action
            else:
                self.player.bonus_action = 0       #Bonus Action used
                if self.is_cantrip == False:
                    self.player.has_cast_left = False
                return True
            
        #Action Spell
        else:
            #Quickened Spell
            if self.player.quickened_spell == 1:
                #Bonus Action free?
                if self.player.bonus_action == 1:
                    #Cast Spell as quickened BA
                    self.player.bonus_action = 0
                    self.player.quickened_spell = 0
                    if self.is_cantrip == False:
                        self.player.has_cast_left = False
                    return True
                #No Bonus Action left
                else:
                    print(self.player.name + ' tried to quickened cast ' + self.spell_name + ', but has no Bonus Action left')
                    quit()
            #No Quickened Spell
            else:
                if self.player.action == 0:
                    self.DM.say(self.player.name + ' tried to cast ' + self.spell_name + ', but has no action left', True)
                    return False
                else:
                    self.player.action = 0  #action used
                    if self.is_cantrip == False:
                        self.player.has_cast_left = False
                    return True

#-------------Meta Magic------------------
    #The mega magic functions do their job and then cast the individual spell
    #See cast function in subclasses
    #the twin_cast function needs exectly two targets
    def twin_cast(self, targets, cast_level=False):
        rules = [len(targets)==2,
                self.player.knows_twinned_spell,
                self.player.sorcery_points >= 2]
        errors = [self.player.name + ' tried to twinned spell ' + self.spell_name + ' but not with 2 targets',
                self.player.name + ' tried to twinned cast ' + self.spell_name + ' without knwoing it',
                self.player.name + ' tried to twinned cast ' + self.spell_name + ' but has not enough sorcery points']
        ifstatements(rules, errors, self.DM).check()
        #If twinned spell is known and sorcery Points there, cast spell twice 
        if self.make_action_check() == True:
            #player should be able to cast, so a True came back. But in the macke_action_check function the bonus_action, action, and/or cast was diabled, so it will be enabled here before casting 
            if cast_level==False:
                cast_level = self.spell_level
            if cast_level == 0:
                self.player.sorcery_points -= 1
            else:
                self.player.sorcery_points -= cast_level
                self.player.spell_slot_counter[cast_level -1] += 1 #add another spell Slots as two will be used in the twin cast
            self.DM.say(self.player.name + ' twinned casts ' + self.spell_name, True)
            if self.is_concentration_spell and self.is_twin_castable:
                #Must enable these here again, as they are disabled in make_action_check()
                if self.is_bonus_action_spell:
                    self.player.bonus_action = 1
                else:
                    self.player.action = 1
                if self.is_cantrip == False:
                    self.player.has_cast_left = True
                #This kind of spells must handle their twin cast in the cast function
                self.cast(targets, cast_level, twinned=True)
            else:
                for x in targets:
                    #everything will be enabeled in order for the spell do be cast twice
                    if self.is_bonus_action_spell:
                        self.player.bonus_action = 1
                    else:
                        self.player.action = 1
                    if self.is_cantrip == False:
                        self.player.has_cast_left = True
                    self.cast(x, cast_level)

    def quickened_cast(self, targets, cast_level=False):
        rules = [self.player.knows_quickened_spell,
                self.player.sorcery_points >= 2,
                self.player.quickened_spell==0]
        errors = [self.player.name + ' tried to use Quickened Spell without knowing it',
                self.player.name + ' tried to use quickened Spell, but has no Sorcery Points left',
                self.player.name + ' tried to use quickened spell, but has already used it']
        ifstatements(rules, errors, self.player.DM).check()

        self.player.sorcery_points -= 2
        self.player.quickened_spell = 1  #see make_spell_check
        self.DM.say(self.player.name + ' used Quickened Spell', True)
        if cast_level==False:
            cast_level = self.spell_level
        self.cast(targets, cast_level)

#---------------DMG Scores---------------
#This Scores are returned to the choose_spell_AI function and should resemble about 
#the dmg that the spell makes or an appropriate counter value if the spell does not 
#make direkt dmg, like haste or entangle
#The Function must also return the choosen Targets and Cast Level
#If a Score 0 is returned the spell will not be considered to be cast that way
#The individual sores are in the subclasses

    def hit_propability(self, target):
    #This function evaluetes how propable a hit with a spell attack will be
        SpellToHit = self.player.spell_mod + self.player.proficiency
        AC = target.AC
        prop = (20 - AC + SpellToHit)/20
        return prop

    def save_sucess_propability(self, target):
        SaveMod = target.modifier[self.spell_save_type]
        Advantage = target.check_advantage(self.spell_save_type, notSilent = False)
        #Save Sucess Propability:
        prop = (20 - self.player.spell_dc + SaveMod)/20
        if Advantage < 0:
            prop = prop*prop  #Disadvantage, got to get it twice
        elif Advantage > 0:
            prop = 1 - (1-prop)**2  #would have to miss twice
        return prop

    def dmg_score(self, SpellTargets, CastLevel, SpellAttack=True, SpellSave=False):
        #This returns a dmg score for the score functions
        DMGScore = 0
        dmg = self.spell_dmg(CastLevel) #is defined in the subclasses that need it
        for target in SpellTargets:
            target_dmg = dmg
            if SpellSave: #Prop that target makes save
                target_dmg = dmg/2 + (dmg/2)*(1-self.save_sucess_propability(target))
            if SpellAttack:   #it you attack, account for hit propabiltiy
                target_dmg = target_dmg*self.hit_propability(target)#accounts for AC
            #DMG Type, Resistances and stuff
            if self.dmg_type in target.damage_vulnerability:
                target_dmg = target_dmg*2
            elif self.dmg_type in target.damage_resistances:
                target_dmg = target_dmg/2
            elif self.dmg_type in target.damage_immunity:
                target_dmg = 0
            DMGScore += target_dmg #Add this dmg to Score

            #Account for Hex
            if target.is_hexed and self.player.is_hexing:
                for HexToken in self.player.CurrentHexToken.links: #This is your Hex target
                    if HexToken.TM.player == target:
                        DMGScore += 3.5
                        break
            #Account for Hunters Mark
            if target.is_hunters_marked and self.player.is_hunters_marking:
                for Token in self.player.CurrentHuntersMarkToken.links: #This is your HM target
                    if Token.TM.player == target:
                        DMGScore += 3.5
                        break


        return DMGScore

    def return_0_score(self):
        #this function returns a 0 score, so that spell is not cast
        Score = 0
        SpellTargets = [self.player]
        CastLevel = 0
        return Score, SpellTargets, CastLevel

    def random_score_scale(self):
        Scale = 0.6+0.8*random()
        return Scale

    def choose_smallest_slot(self, MinLevel, MaxLevel):
        #Returns the smallest spellslot that is still available in the range
        #MaxLevel is cast level, so MaxLevel = 4 means Level 4 Slot
        #False, no Spell Slot available
        if MaxLevel > 9: MaxLevel = 9
        if MinLevel < 1: MinLevel = 1
        for i in range(MinLevel-1, MaxLevel):
            if self.player.spell_slot_counter[i]>0:  #i = 0 -> lv1 slot
                return i+1
        return False 

    def choose_highest_slot(self, MinLevel, MaxLevel):
        #Returns the highest spellslot that is still available in the range
        #MinLevel is cast level, so MinLevel = 4 means Level 4 Slot
        #False, no Spell Slot available
        if MaxLevel > 9: MaxLevel = 9
        if MinLevel < 1: MinLevel = 1
        for i in reversed(range(MinLevel-1, MaxLevel)):
            if self.player.spell_slot_counter[i]>0:
                return i+1
        return False 

#Specialized Spell Types
class attack_spell(spell):
    #This Class is a spell that makes one or more single target spell attacks
    def __init__(self, player, dmg_type, number_of_attacks = 1):
        super().__init__(player)
        self.number_of_attacks = number_of_attacks
        self.dmg_type = dmg_type
        self.spell_text = 'spell name' #This will be written as the spell name in print
    
    def cast(self, targets, cast_level=False, twinned=False):
        if type(targets) != list:
            targets = [targets]  #if a list, take first target
        super().cast(targets, cast_level, twinned) #self.cast_level is set in spell super.cast
        #Cast is authorized, so make a spell attack
        tohit = self.player.spell_mod + self.player.proficiency
        dmg = self.spell_dmg(self.cast_level)

        if self.player.empowered_spell:
            dmg = dmg*1.21
            self.player.empowered_spell = False #reset empowered spell
            self.DM.say(' Empowered: ')

        #Everything is set up and in order
        #Now make the attack/attacks       
        return self.make_spell_attack(targets, dmg, tohit)

    def make_spell_attack(self,targets, dmg, tohit):
        #This function is called in cast function and makes the spell attacks
        #all specifications for this spell are given to the attack function
        #Can attack multiple targts, if one target is passed and num of attacks == 1 this is just one attack
        target_counter = 0
        attack_counter = self.number_of_attacks
        dmg_dealed = 0
        while attack_counter > 0:
            dmg_dealed += self.player.attack(targets[target_counter], is_ranged=self.is_range_spell, other_dmg=dmg, damage_type=self.dmg_type, tohit=tohit, is_spell=True)
            attack_counter -= 1
            target_counter += 1
            if target_counter == len(targets):
                target_counter = 0  #if all targets were attacked once, return to first
        return dmg_dealed

    def spell_dmg(self, cast_level):
        #This function will return the dmg according to Cast Level
        print('No dmg defined for spell: ' + self.spell_name)

    def score(self, fight, twinned_cast=False):
        #This function takes an attack spell and chooses targets and a cast level
        #It then returns an expactation damage score for the choice class
        #Choose CastLevel:
        if self.is_cantrip: CastLevel = 0
        else:
            CastLevel = self.choose_highest_slot(self.spell_level,9) #Choose highest Spell Slot
            if CastLevel == False: return self.return_0_score()

        #Find a suitable target/targts for this spell
        Choices = [x for x in fight if x.team != self.player.team]
        SpellTargets = []
        for i in range(0,self.number_of_attacks):
            #Append as many targets as attack numbers
            SpellTarget = self.player.AI.choose_att_target(Choices, AttackIsRanged=self.is_range_spell, other_dmg = self.spell_dmg(CastLevel), other_dmg_type=self.dmg_type, is_silent=True)
            if SpellTarget == False: #No target found
                return self.return_0_score()
            else: SpellTargets.append(SpellTarget)

        #Twin Cast
        if twinned_cast:
            if all([self.is_twin_castable, self.number_of_attacks == 1]):
                Choices.remove(SpellTargets[0]) #do not double twin cast
                TwinTarget = self.player.AI.choose_att_target(Choices, AttackIsRanged=self.is_range_spell, other_dmg = self.spell_dmg(CastLevel), other_dmg_type=self.dmg_type, is_silent=True)
                if TwinTarget == False: return self.return_0_score()  #No Target found
                SpellTargets.append(TwinTarget)
            else:
                print(self.player.name + ' requested twincast score, but target number does not check out')
                quit()

        #DMG Score
        Score = 0
        Score += self.dmg_score(SpellTargets, CastLevel, SpellAttack=True, SpellSave=False)
        if twinned_cast: Score = Score*2

        Score = Score*self.random_score_scale()  #a little random power
        return Score, SpellTargets, CastLevel

class save_spell(spell):
    #This Class is a spell that makes one target make a spell save check
    #If it fails the save, an effect occures
    def __init__(self, player, spell_save_type):
        #spell save type is what check they make
        super().__init__(player)
        self.spell_save_type = spell_save_type
        self.spell_text = 'spell name' #This will be written as the spell name in print

    def cast(self, target, cast_level=False, twinned=False):
        super().cast(target, cast_level, twinned)
        self.make_save(self, target, twinned)

    def make_save(self, target, twinned):
        #Single Target only
        if type(target) == list:
            target = target[0]
        
        target.last_attacker = self.player #target remembers last attacker/spell
        save = target.make_save(self.spell_save_type, DC = self.player.spell_dc) #make the save
        if save < self.player.spell_dc:
            #If failed, then take the individual effect
            self.DM.say(': failed the save')
            self.take_effect(target, twinned)
        else:
            self.DM.say(': made the save')
    
    def take_effect(self, target, twinned):
        #Take effect on a single target
        #This must be implemented in the subclasses
        print('The Save Spell has no effect')
        quit()

class aoe_dmg_spell(spell):
    #This class is a spell that targts multiple targts with a AOE dmg spell
    #On a Save the target gets half dmg
    def __init__(self, player, spell_save_type, dmg_type, aoe_area):
        super().__init__(player)
        self.spell_save_type = spell_save_type #What kind of save
        self.dmg_type = dmg_type
        self.spell_text = 'spell name' #This will be written as the spell name in print
        self.aoe_area = aoe_area  #area of the AOE in ft**2

    def cast(self, targets, cast_level=False, twinned=False):
        #Multiple Targts
        if type(targets) != list: targets = [targets]
        super().cast(targets, cast_level, twinned) #self.cast_level now set in spell super cast

        #Damage and empowered Spell
        damage = self.spell_dmg(self.cast_level)
        if self.player.empowered_spell:
            damage = damage*1.21
            self.player.empowered_spell = False
            self.DM.say(' Empowered: ')

        for target in targets:
            #Every target makes save
            self.make_save_for(target, damage=damage)

    def make_save_for(self, target, damage):
        #This function is called for every target to make the save and apply the dmg
        save = target.make_save(self.spell_save_type,DC = self.player.spell_dc)
        if save >= self.player.spell_dc:
            self.apply_dmg(target, damage=damage/2)
        else: self.apply_dmg(target, damage=damage)

    def apply_dmg(self, target, damage):
        #This finally applies the dmg dealed
        dmg_to_apply = dmg(damage, self.dmg_type)
        target.last_attacker = self.player
        target.changeCHP(dmg_to_apply, self.player, True)

    def spell_dmg(self, cast_level):
        #This function will return the dmg according to Cast Level
        print('No dmg defined for spell: ' + self.spell_name)

    def score(self, fight, twinned_cast=False):
        #This function takes an AOE spell and chooses targets and a cast level
        #It then returns an expactation damage score for the choice class
        #Choose CastLevel:
        if self.is_cantrip: CastLevel = 0
        else:
            CastLevel = self.choose_highest_slot(self.spell_level,9) #Choose highest Spell Slot
            if CastLevel == False: return self.return_0_score()

        #Find suitable targts for this spell
        SpellTargets = self.player.AI.area_of_effect_chooser(fight, self.aoe_area)

        #DMG Score
        Score = self.dmg_score(SpellTargets, CastLevel, SpellAttack=False, SpellSave=True)
        Score = Score*self.random_score_scale()  #a little random power
        return Score, SpellTargets, CastLevel

#Specific Spells
#Cantrips
class firebolt(attack_spell):
    def __init__(self, player):
        dmg_type = 'fire'
        self.spell_name = 'FireBolt'
        super().__init__(player, dmg_type)
        self.spell_text = 'fire bolt'
        self.spell_level = 0
        self.is_cantrip = True
        self.is_range_spell = True
        self.is_twin_castable = True
    
    def spell_dmg(self, cast_level):
        self.firebolt_dmg = 0
        if self.player.level < 5:
            self.firebolt_dmg = 5.5
        elif self.player.level < 11:
            self.firebolt_dmg = 5.5*2
        elif self.player.level < 17:
            self.firebolt_dmg = 5.5*3
        else:
            self.firebolt_dmg = 5.5*4
        return self.firebolt_dmg

class chill_touch(attack_spell):
    def __init__(self, player):
        dmg_type = 'necrotic'
        self.spell_name = 'ChillTouch'

        super().__init__(player, dmg_type)
        self.spell_text = 'chill touch'
        self.spell_level = 0
        self.is_cantrip = True
        self.is_range_spell = False
        self.is_twin_castable = True

    def spell_dmg(self, cast_level):
        self.chill_touch_dmg = 0
        #Calculate DMG
        if self.player.level < 5:
            self.chill_touch_dmg = 4.5
        elif self.player.level < 11:
            self.chill_touch_dmg = 4.5*2
        elif self.player.level < 17:
            self.chill_touch_dmg = 4.5*3
        else:
            self.chill_touch_dmg = 4.5*4
        return self.chill_touch_dmg
    
    def cast(self, target, cast_level=0, twinned=False):
        #class cast function returns dealed dmg
        dmg_dealed = super().cast(target, cast_level, twinned)

        if type(target) == list: target = target[0]
        if dmg_dealed > 0:
            target.chill_touched = True
            self.DM.say(str(target.name) + ' was chill touched', True)
    
    def score(self, fight, twinned_cast=False):
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        Score += SpellTargets[0].heal_given/8 #for the anti heal effect
        Score += SpellTargets[0].start_of_turn_heal #if the target gets heat at start of turn
        return Score, SpellTargets, CastLevel

class eldritch_blast(attack_spell):
    def __init__(self, player):
        dmg_type = 'force'
        self.spell_name = 'EldritchBlast'
        super().__init__(player, dmg_type)

        #Number of attacks at higher level 
        if player.level < 5:
            self.number_of_attacks = 1
        elif player.level < 11:
            self.number_of_attacks = 2
        elif player.level < 17:
            self.number_of_attacks = 3
        else:
            self.number_of_attacks = 4

        self.spell_text = 'eldritch blast'
        self.spell_level = 0
        self.is_cantrip = True
        self.is_range_spell = True
        self.is_twin_castable = False
    
    def spell_dmg(self, cast_level):
        damage = 5.5 #1d10
        #Aganizing Blast
        if self.player.knows_agonizing_blast:
            damage += self.player.modifier[5] #Add Cha Mod
        return damage

    def announce_cast(self):
        super().announce_cast()
        if self.player.knows_agonizing_blast:
            self.DM.say(', Agonizing: ')

#1-Level Spell
class burning_hands(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'BurningHands'
        super().__init__(player, spell_save_type, dmg_type='fire', aoe_area=115) #15ft^2/2
        self.spell_text = 'burning hands'
        self.spell_level = 1
        self.is_range_spell = True

    def spell_dmg(self, cast_level):
        #Return the spell dmg
        damage = 10.5 + 3.5*(cast_level-1)   #upcast dmg 3d6 + 1d6 per level over 2
        return damage

class magic_missile(spell):
    def __init__(self, player):
        self.spell_name = 'MagicMissile'
        super().__init__(player)
        self.spell_text = 'magic missile'
        self.spell_level = 1
        self.is_range_spell = True
        self.dmg_type = 'force'
    
    def cast(self, targets, cast_level=False, twinned=False):
        damage = 3.5   #1d4 + 1
        if self.player.empowered_spell:
            damage = damage*1.21
            self.player.empowered_spell = False
            self.DM.say(' Empowered: ')
        super().cast(targets, cast_level, twinned)
        if type(targets) != list: targets = [targets]
        self.hurl_missile(targets, damage)

    def hurl_missile(self, targets, damage):
        missile_counter = 2 + self.cast_level          #overcast mag. mis. for more darts 
        target_counter = 0
        while missile_counter > 0:    #loop for missile cast
            missile_counter -= 1
            Dmg = dmg(damage, 'force')
            #Check for Tokens Trigger
            self.player.TM.hasHitWithAttack(targets[target_counter], Dmg, is_ranged=True, is_spell=True)
            targets[target_counter].TM.washitWithAttack(self.player, Dmg, is_ranged=True, is_spell=True)

            targets[target_counter].last_attacker = self.player    #target remembers last attacker
            targets[target_counter].changeCHP(Dmg, self.player, True)    #target takes damage
            target_counter += 1
            if target_counter == len(targets):    #if all targets are hit once, restart 
                target_counter = 0

    def score(self, fight, twinned_cast=False):
        CastLevel = self.choose_highest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        TargetNumer = CastLevel + 2
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5, other_dmg_type='force') for i in range(0, TargetNumer)]
        if False in SpellTargets:
            return self.return_0_score()

        #DMG Score
        Score = self.dmg_score(SpellTargets, CastLevel, SpellAttack=False)
        Score += 2*CastLevel #a little extra for save hit
        Score = Score*self.random_score_scale() # +/-20% range to vary spells
        return Score, SpellTargets, CastLevel

    def spell_dmg(self, cast_level):
        return 3.5

class guiding_bolt(attack_spell):
    def __init__(self, player):
        dmg_type = 'radiant'
        self.spell_name = 'GuidingBolt'
        super().__init__(player, dmg_type)
        self.spell_text = 'guiding bolt'
        self.spell_level = 1
        self.is_twin_castable = True
        self.is_range_spell = True

    def cast(self, target, cast_level=False, twinned=False):
        if type(target) == list: target = target[0]
        dmg_dealed = super().cast(target, cast_level, twinned)

        #On hit:
        if dmg_dealed > 0:
            LinkToken = GuidingBoltedToken(target.TM) #Target gets guiding bolted token
            GuidingBoltToken(self.TM, [LinkToken]) #Timer Dock Token for player
   
    def spell_dmg(self, cast_level):
        return 14 + 3.5*(cast_level-1) #3d10 + 1d10/level > 1

    def score(self, fight, twinned_cast=False):
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        if Score != 0:
            Score += SpellTargets[0].dps()*0.2 #to account for advantage given
        return Score, SpellTargets, CastLevel

class entangle(save_spell):
    def __init__(self, player):
        spell_save_type = 0 #str
        self.spell_name = 'Entangle'
        super().__init__(player, spell_save_type)
        self.spell_text = 'entangle'
        self.spell_level = 1
        self.is_twin_castable = True
        self.is_concentration_spell = True
        self.is_range_spell = True
    
    def cast(self, targets, cast_level=False, twinned=False):
        #Rewrite cast function to be suited for entangle
        #Entangle takes one target, or two if twinned
        if len(targets) > 2 or len(targets) == 2 and twinned == False: 
            print('Too many entangle targets')
            quit()
        if cast_level == False: cast_level = self.spell_level
        self.autorize_cast(cast_level) #self.cast_level now set
        self.player.DM.say(self.player.name + ' casts ' + self.spell_text, True)

        self.EntangleTokens = [] #List for entagle Tokens
        for target in targets:
            self.make_save(target, twinned)  #This triggeres the super class make save function, if failed the take_effect function is called
            #Here self.EntangleTokens is filled with tokens if it takes effect
        if len(self.EntangleTokens) != 0:
            ConcentrationToken(self.TM, self.EntangleTokens)
            #player is concentrating on a Entagled Target or targets

    def take_effect(self, target, twinned):
        EntangleToken = EntangledToken(target.TM, subtype='r') #Target gets a entangled token
        self.EntangleTokens.append(EntangleToken) #Append to list

    def score(self, fight, twinned_cast=False):
        #Find lowest spellslot to cast
        CastLevel = self.choose_smallest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        TargetNumber = 1
        if twinned_cast: TargetNumber = 2

        TargetChoices = fight.copy() #to remove from
        SpellTargets = []
        for i in range(0,TargetNumber): #choose 1-2 targets
            Target = self.player.AI.choose_att_target(TargetChoices, AttackIsRanged=True, other_dmg=0, other_dmg_type='true', is_silent=True) # Find target for entangle
            if Target == False: return self.return_0_score() #no target
            else:
                SpellTargets.append(Target)
                TargetChoices.remove(Target) #Dont double cast
        Score = 0
        
        for x in SpellTargets:
            Score += x.dps()/4 #disadvantage helps do reduce dmg of enemy
            #Add dmg for the other players
            Score += self.player.spell_dc - 10 - x.modifier[0] #good against weak enemies
            if x.restrained: Score = 0 #Do not cast on restrained targets
        if self.player.knows_wild_shape: Score = Score*1.2 #good to cast before wild shape
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

class cure_wounds(spell):
    def __init__(self, player):
        self.spell_name = 'CureWounds'
        super().__init__(player)
        self.spell_text = 'cure wounds'
        self.spell_level = 1
        self.is_twin_castable = True
    
    def cast(self, target, cast_level=False, twinned=False):
        if type(target) == list: target = target[0]
        super().cast(target, cast_level, twinned) #self.cast_level now set
        heal = 4.5*self.cast_level + self.player.spell_mod
#        self.DM.say(self.player.name + ' touches ' + target.name + ' with magic:')
        target.changeCHP(dmg(-heal, 'heal'), self.player, False)

class healing_word(spell):
    def __init__(self, player):
        self.spell_name = 'HealingWord'
        super().__init__(player)
        self.spell_text = 'healing word'
        self.spell_level = 1
        self.is_twin_castable = True
        self.is_range_spell = True
        self.is_bonus_action_spell = True
    
    def cast(self, target, cast_level=False, twinned=False):
        if type(target) == list: target = target[0]
        super().cast(target, cast_level, twinned) #self.cast_level now set
        heal = 2.5*self.cast_level + self.player.spell_mod
        if heal < 0: heal = 1
#        self.DM.say(self.player.name + ' speaks to ' + target.name)
        target.changeCHP(dmg(-heal, 'heal'), self.player, True)

class hex(spell):
    def __init__(self, player):
        self.spell_name = 'Hex'
        super().__init__(player)
        self.spell_text = 'hex'
        self.spell_level = 1
        self.is_bonus_action_spell = True
        self.is_twin_castable = False
        self.is_range_spell = True
        self.is_concentration_spell = True
    
    def cast(self, target, cast_level=False, twinned=False):
        if type(target) == list: target = target[0]
        super().cast(target, cast_level, twinned)
        HexToken = HexedToken(target.TM, subtype='hex') #hex the Tagret
        self.player.CurrentHexToken = HexingToken(self.TM, HexToken) #Concentration on the caster
        #Assign that Token as the Current HEx Token of the Player

    def change_hex(self, target):
        rules = [self.player.can_choose_new_hex,
                self.is_known,
                target.state == 1,
                self.player.bonus_action == 1]
        errors = [self.player.name + ' tried to change a bound hex',
                self.player.name + ' tried to change a hex without knowing it',
                self.player.name + ' tried to change to a not conscious target',
                self.player.name + ' tried to change a hex without having a bonus action']
        ifstatements(rules, errors, self.DM).check()

        self.DM.say(self.player.name + ' changes the hex to ' + target.name, True)
        self.player.bonus_action = 0 #takes a BA
        self.player.can_choose_new_hex = False
        NewHexToken = HexedToken(target.TM, subtype='hex') #hex the Tagret
        self.player.CurrentHexToken.addLink(NewHexToken) #Add the new Hex Token

    def score(self, fight, twinned_cast=False):
        SpellTarget = self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5, other_dmg_type='necrotic', is_silent=True) #Choose best target
        if SpellTarget == False: return self.return_0_score()

        Score = 0
        attacks = self.player.attacks
        if 'EldritchBlast' in self.player.SpellBook:
            Score += 3.5 #A warlock would want to cast hex
            attacks = self.player.SpellBook['EldritchBlast'].number_of_attacks
        Score = 3.5*attacks*(random()*3 + 2) #hex holds for some rounds
        if 'MagicMissile' in self.player.SpellBook:
            Score += 3.5 #Mag Missile Combi

        CastLevel = self.choose_smallest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTarget, CastLevel 

class hunters_mark(spell):
    def __init__(self, player):
        self.spell_name = 'HuntersMark'
        super().__init__(player)
        self.spell_text = 'hunters mark'
        self.spell_level = 1
        self.is_bonus_action_spell = True
        self.is_twin_castable = False
        self.is_range_spell = True
        self.is_concentration_spell = True
    
    def cast(self, target, cast_level=False, twinned=False):
        if type(target) == list: target = target[0]
        super().cast(target, cast_level, twinned)
        self.DM.say(' at ' + target.name)
        HuntersMarkToken = HuntersMarkedToken(target.TM, subtype='hm') #hunters mark the Tagret
        self.player.CurrentHuntersMarkToken = HuntersMarkingToken(self.TM, HuntersMarkToken) #Concentration on the caster
        #Assign that Token as the Current Hunters Mark Token of the Player

    def announce_cast(self):
        text = ''.join([self.player.name,' casts ',self.spell_text,' at lv.',str(self.cast_level)])
        self.player.DM.say(text, True)

    def change_hunters_mark(self, target):
        rules = [self.player.can_choose_new_hunters_mark,
                self.is_known,
                target.state == 1,
                self.player.bonus_action == 1]
        errors = [self.player.name + ' tried to change a bound hunters mark',
                self.player.name + ' tried to change a hunters mark without knowing it',
                self.player.name + ' tried to change to a not conscious target',
                self.player.name + ' tried to change a hunters mark without having a bonus action']
        ifstatements(rules, errors, self.DM).check()

        self.DM.say(self.player.name + ' changes the hunters mark to ' + target.name, True)
        self.player.bonus_action = 0 #takes a BA
        self.player.can_choose_new_hunters_mark = False
        NewHuntersMarkToken = HuntersMarkedToken(target.TM, subtype='hm') #hunters mark the Tagret
        self.player.CurrentHuntersMarkToken.addLink(NewHuntersMarkToken) #Add the new Token

    def score(self, fight, twinned_cast=False):
        SpellTarget = self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=3.5, other_dmg_type=self.TM.player.damage_type, is_silent=True) #Choose best target
        if SpellTarget == False: return self.return_0_score()

        Score = 0
        attacks = self.player.attacks
        Score = 3.5*attacks*(random()*3 + 2) #hunters mark holds for some rounds
        if 'MagicMissile' in self.player.SpellBook:
            Score += 3.5 #Mag Missile Combi

        CastLevel = self.choose_smallest_slot(1,9)
        if CastLevel == False: return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTarget, CastLevel 

class armor_of_agathys(spell):
    def __init__(self, player):
        self.spell_name = 'ArmorOfAgathys'
        super().__init__(player)
        self.spell_text = 'armor of agathys'
        self.spell_level = 1
    
    def cast(self, target, cast_level=False, twinned=False):
        super().cast(target, cast_level, twinned)
        player = self.player
        player.has_armor_of_agathys = True
        TempHP = 5*self.cast_level
        player.agathys_dmg = TempHP
        player.addTHP(TempHP) #add THP to self

    def score(self, fight, twinned_cast=False):
        player = self.player
        SpellTargets = [player] #only self cast

        #Choose Slot
        Highest_Slot = self.choose_highest_slot(1,9)
        if Highest_Slot != False:
            CastLevel = self.choose_highest_slot(1,Highest_Slot-1) #Not use your highest slot
            if CastLevel == False:
                return self.return_0_score()
        else: return self.return_0_score()

        if player.has_armor_of_agathys: return self.return_0_score() #no double cast
        
        Score = 10*CastLevel #does at least 5dmg and 5 TPH for you
        Score = Score*(3 - 2*player.CHP/player.HP) #tripples for low player
        Score -= player.THP*2 #If you still have THP, rather keep it

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel
 
class false_life(spell):
    def __init__(self, player):
        self.spell_name = 'FalseLife'
        super().__init__(player)
        self.spell_text = 'false life'
        self.spell_level = 1
    
    def cast(self, target, cast_level=False, twinned=False):
        super().cast(target, cast_level, twinned)
        TempHP = 1.5 + 5*self.cast_level
        self.player.addTHP(TempHP) #Add the THP

    def score(self, fight, twinned_cast=False):
        player = self.player
        SpellTargets = [player] #only self cast

        #Choose Slot
        Highest_Slot = self.choose_highest_slot(1,9)
        if Highest_Slot != False:
            CastLevel = self.choose_highest_slot(1,Highest_Slot-1) #Not use your highest slot
            if CastLevel == False:
                return self.return_0_score()
        else: return self.return_0_score()

        #Score 
        Score = 1.5 + 3*CastLevel  #dmg equal value but for THP, a bit lower then 5
        Score = Score*(3 - 2*player.CHP/player.HP) #tripples for low player
        if player.THP > 0:
            return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

class shield(spell):
    def __init__(self, player):
        self.spell_name = 'Shield'
        super().__init__(player)
        self.spell_text = 'shield'
        self.spell_level = 1
        self.is_reaction_spell = True
    
    def cast(self, target=False, cast_level=False, twinned=False):
        super().cast(target, cast_level, twinned)
        self.player.AC += 5
        #Shield does not ware of when unconscious, but I think that is actually correct

    def announce_cast(self):
        super().announce_cast()
        self.DM.say(' ') #for printing in attacks so it fits with next print

class inflict_wounds(attack_spell):
    def __init__(self, player):
        dmg_type = 'necrotic'
        self.spell_name = 'InflictWounds'
        super().__init__(player, dmg_type)
        self.spell_text = 'inflict wounds'
        self.spell_level = 1
        self.is_twin_castable = True
    
    def spell_dmg(self, cast_level):
        return 16.5 + 5.5*(cast_level-1) #3d10 + 1d10/level > 1

#2-Level Spell

class scorching_ray(attack_spell):
    def __init__(self, player):
        dmg_type = 'fire'
        self.spell_name = 'ScorchingRay'
        super().__init__(player, dmg_type)
        self.spell_text = 'scorching ray'
        self.spell_level = 2
        self.is_range_spell = True
    
    def spell_dmg(self, cast_level):
        return 7 #2d6 dmg per ray

    def cast(self, targets, cast_level=False, twinned=False):
        if cast_level == False: cast_level = self.spell_level
        self.number_of_attacks = 1 + cast_level
        #Set the number of attacks, then let the super cast function handle the rest
        super().cast(targets, cast_level, twinned)

class aganazzars_sorcher(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'AganazzarsSorcher'
        super().__init__(player, spell_save_type, dmg_type='fire', aoe_area=300) #30ft*10ft 
        self.spell_text = 'aganazzars scorcher'
        self.spell_level = 2
        self.is_range_spell = True

    def spell_dmg(self, cast_level):
        #Return the spell dmg
        damage = 13.5 + 4.5*(cast_level-2)   #upcast dmg 3d8 + 1d8 per level over 2
        return damage

class shatter(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 2 #Con
        self.spell_name = 'Shatter'
        super().__init__(player, spell_save_type, dmg_type='thunder', aoe_area=315) #pi*10ft^2
        self.spell_text = 'shatter'
        self.spell_level = 2
        self.is_range_spell = True

    def spell_dmg(self, cast_level):
        #Return the spell dmg
        damage = 13.5 + 4.5*(cast_level-2)   #upcast dmg 3d8 + 1d8 per level over 2
        return damage

class spiritual_weapon(spell):
    def __init__(self, player):
        self.spell_name = 'SpiritualWeapon'
        super().__init__(player)
        self.spell_text = 'spiritual weapon'
        self.spell_level = 1
        self.dmg_type = 'force'
    
    def cast(self, target, cast_level=False, twinned=False):
        super().cast(target, cast_level, twinned)
        #remember, if use cast level, use self.cast_level not cast_level
        player = self.player
        player.has_spiritual_weapon = True
        player.SpiritualWeaponDmg = player.spell_mod + 4.5*(self.cast_level -1) 
        player.SpiritualWeaponCounter = 0 #10 Rounds of Weapon

        #If a player cast this spell for the first time, the choice will be aded to the AI
        #The Score function will still check if the player is allowed to use it
        if player.AI.spiritualWeaponChoice not in player.AI.Choices:
            player.AI.Choices.append(player.AI.spiritualWeaponChoice)

        #Attack Once as BA
        if player.bonus_action == 1:
            self.spiritual_weapon_attack(target)

    def use_spiritual_weapon(self, target):
        player = self.player
        rules = [player.has_spiritual_weapon,
                player.bonus_action == 1]
        errors = [player.name + ' tried using the Spiritual Weapon without having one',
                player.name + ' tried using the Spiritual Weapon without having a bonus action']
        ifstatements(rules, errors, self.DM).check()

        self.spiritual_weapon_attack(target)

    def spiritual_weapon_attack(self, target):
        if type(target) == list:
            target = target[0]
        player = self.player
        WeaponTohit = player.spell_mod + player.proficiency #ToHit of weapon
        WeaponDmg = player.SpiritualWeaponDmg #Set by the Spell 
        self.DM.say('Spiritual Weapon of ' + player.name + ' attacks: ', True)
        #Make a weapon Attack against first target
        self.player.attack(target, is_ranged=False, other_dmg=WeaponDmg, damage_type='force', tohit=WeaponTohit, is_spell=True)
        self.player.bonus_action = 0 #It uses the BA to attack

    def spell_dmg(self, cast_level):
        return self.player.spell_mod + 4.5*(cast_level - 1)

    def score(self, fight, twinned_cast=False):
        player = self.player

        if player.has_spiritual_weapon:
            return self.return_0_score() #has already sw 

        #Choose Slot
        Highest_Slot = self.choose_highest_slot(2,9) 
        if Highest_Slot != False:
            CastLevel = self.choose_highest_slot(2,Highest_Slot-1) #Not use your highest slot
            if CastLevel == False:
                return self.return_0_score()
        else: return self.return_0_score()

        #Choose Target for first attack
        SpellTargets = [self.player.AI.choose_att_target(fight, AttackIsRanged=True, other_dmg=self.spell_dmg(CastLevel), other_dmg_type=self.dmg_type, is_silent=True)]
        if SpellTargets[0] == False:
            return self.return_0_score()#no Enemy in reach


        Score = self.dmg_score(SpellTargets, CastLevel, SpellAttack=True)
        Score = Score*(2 + 2*random()) #expecting to hit with it multiple times
        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

#3-Level Spell
class fireball(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'Fireball'
        super().__init__(player, spell_save_type, dmg_type='fire', aoe_area=1250) #pi*20ft**2
        self.spell_text = 'fireball'
        self.spell_level = 3
        self.is_range_spell = True

    def spell_dmg(self, cast_level):
        #Return the spell dmg
        damage = 28 + 3.5*(cast_level-3)   #upcast dmg 8d6 + 1d6 per level over 2
        return damage

class lightningBolt(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'LightningBolt'
        super().__init__(player, spell_save_type, dmg_type='lightning', aoe_area=1000) #100ft*10ft
        self.spell_text = 'lightning bolt'
        self.spell_level = 3
        self.is_range_spell = True

    def spell_dmg(self, cast_level):
        #Return the spell dmg
        damage = 28 + 3.5*(cast_level-3)   #upcast dmg 3d6 + 1d6 per level over 2
        return damage

class haste(spell):
    def __init__(self, player):
        self.spell_name = 'Haste'
        super().__init__(player)
        self.spell_text = 'haste'
        self.spell_level = 3
        self.is_twin_castable = True
        self.is_concentration_spell = True
        self.is_range_spell = True
    
    def cast(self, targets, cast_level=False, twinned=False):
        if len(targets) > 2 or len(targets) == 2 and twinned == False: 
            print('Too many entangle targets')
            quit()
        super().cast(targets, cast_level, twinned)
        HasteTokens = []
        for target in targets:
            HasteToken = HastedToken(target.TM, subtype='h')
            HasteTokens.append(HasteToken)
            self.DM.say(self.player.name + ' gives haste to ' + target.name, True)
        ConcentrationToken(self.TM, HasteTokens)
        #Player is now concentrated on 1-2 Haste Tokens

    def score(self, fight, twinned_cast=False):
        player = self.player
        SpellTargets = []
        Choices = [x for x in fight if x.team == player.team and x.state == 1]
        ChoicesScore = [x.dmg*(random()*0.5 +0.5) + x.AC*(random()*0.2 +0.2) + x.CHP/3*(random()*0.2 + 0.1) for x in Choices]
        SpellTargets.append(Choices[argmax(ChoicesScore)]) #append best player for Haste
        if twinned_cast:
            removeIndex = argmax(ChoicesScore)
            Choices.pop(removeIndex) #Dont double haste
            ChoicesScore.pop(removeIndex)
            if len(Choices) == 0: return self.return_0_score()
            SpellTargets.append(Choices[argmax(ChoicesScore)]) #append best player for 2nd Haste

        Score = 0
        for x in SpellTargets:
            Score += x.dmg/2*(random()*3.5 + 0.7) #lasts for some rounds
            Score += x.AC - player.AC #Encourage High AC
            #Dont haste low Ally
            if x.CHP < x.HP/4:
                Score -= x.dmg
            if x.is_summoned: Score = 0 #do not haste summons

        CastLevel = self.choose_smallest_slot(3,9) #smalles slot 
        if CastLevel == False: return self.return_0_score()

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

class conjure_animals(spell):
    def __init__(self, player):
        self.spell_name = 'ConjureAnimals'
        super().__init__(player)
        self.spell_text = 'conjure animals'
        self.spell_level = 3
        self.is_concentration_spell = True

    def cast(self, fight, cast_level=False, twinned=False):
        #Im am using a trick here, ususally only a target is passed, but this spell needs the fight
        #As a solution the score function of this spell passes the fight as 'targtes' 
        #The cunjured Animals are initiated as fully functunal entity objects
        #The Stats are loaded from the Archive
        #If they reach 0 CHP they will die and not participate in the fight anymore
        #The do_the_fighting function will then pic them out and delete them from the fight list
        super().cast(fight, cast_level, twinned)

        Number, AnimalName = self.choose_animal()
        player = self.player
        #Initiate a new entity for the Animals and add them to the fight
        conjuredAnimals = []
        for i in range(0,Number):
            animal = player.summon_entity(AnimalName, archive=True)
            animal.name = 'Conjured ' + AnimalName + str(i+1)
            self.DM.say(animal.name + ' appears', True)
            animal.summoner = player
            fight.append(animal)

            conjuredAnimals.append(SummenedToken(animal.TM, 'ca')) #add a SummonedToken to the animal
        #Add a Summoner Token to the Player
        SummonerToken(self.TM, conjuredAnimals)

    def choose_animal(self):
        level = 10 #will be set to Beast level for test
        while level > 2:
            Index = int(random()*len(self.player.BeastForms))
            AnimalName = self.player.BeastForms[Index]['Name'] #Random Animal
            level = self.player.BeastForms[Index]['Level'] #Choose a Animal of level 2 or less

        Number = int(2/level)     #8 from CR 1/4, 4 from CR 1/2 ...
        
        if self.cast_level < 5:
            Number = Number
        elif self.cast_level < 7:
            Number = Number*2
        elif self.cast_level < 9: 
            Number = Number*3
        else: 
            Number = Number*4
        
        return Number, AnimalName

    def score(self, fight, twinned_cast=False):
        player = self.player
        SpellTargets = fight #this is a trick to pass the fight to the spell cast function
        #Okay, the critical level are 3, 5, 7, 9
        #So 4, 6, 8 would be a bit wasted
        TryLevel = [9,7,5,3]
        CastLevel = False
        for x in TryLevel:  #find best slot
            if self.player.spell_slot_counter[x-1] > 0:
                CastLevel = x
                break
        if CastLevel == False:
            CastLevel = self.choose_smallest_slot(x,9)

        if CastLevel == False: return self.return_0_score()  #no slot


        Score = 0 #for now
        if player.has_summons:
            print('Has sommons already')
            quit() #nonsense
        #Ape has CR 1/2 with +5 to hit, 6.5 dmg, 2 attacks -> 6.5/4 *2attacks /0.5CR -> 6.5dmg/1CR
        #BrownBear CR 1 +5 9.75dmg, 2 attacks -> 4.8dmg/1CR
        #Wolf 7dmg/4 /0.25CR -> 7dmg/1CR
        #About 6 dmg/1CR, HP matters less because of Concentration

        #As concentration can be interrupted, they might not last so long, lets say 1-3 Rounds
        if CastLevel < 5:
            TotalCR = 2
        elif CastLevel < 7:
            TotalCR = 4
        elif CastLevel < 9: 
            TotalCR = 6
        else: 
            TotalCR = 8
        Score = TotalCR*6*(random()*2 + 1) #CR * 6dmg/CR * 1-3 Rounds
        if self.player.knows_wild_shape: Score = Score*1.3 #good to cast before wild shape
        return Score, SpellTargets, CastLevel

class call_lightning(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'CallLightning'
        super().__init__(player, spell_save_type, dmg_type='lightning', aoe_area=315) #Are 5ft Radius, but 
        self.spell_text = 'call lightning'
        self.spell_level = 3
        self.is_range_spell = True
        self.is_concentration_spell = True
        self.recast_damge = 0

    def cast(self, targets, cast_level=False, twinned=False):
        if cast_level != False: self.recast_damge = self.spell_dmg(cast_level) #set damage for later recast
        else: self.recast_damge = self.spell_dmg(self.spell_level) #level 3 spell
        #Empowered spell does not affect recast, so it checks out 
        super().cast(targets, cast_level, twinned) #Cast Spell as simple AOE once
        #Add Token for late recast
        CallLightningToken(self.TM, [], cast_level) #no links
        #Okay so this has some layers:
        #1. The ClalLightningToken adds the callLightningChoice to the AI (and removes it aswell, when resolved)
        #2. The AI then can use the CallLightningChoice for score and use the Choice to call lighning as recast
        #3. The Choice then uses the players call_lightning spell to recast, which brings it back to this call here
        #Okay not thaaaat many layers, but still

    def recast(self, targets, cast_level=False, twinned=False):
        #Recast the spell laster, if still concentrated
        rules = [self.is_known,
                 self.player.action == 1,
                 self.player.is_concentrating,]
        errors = [self.player.name + ' tried to recast ' + self.spell_name + ', without knowing the spell',
                self.player.name + ' tried to recast ' + self.spell_name + 'but has no action left',
                self.player.name + ' tried to recast ' + self.spell_name + 'but is no longer concentrated']
        ifstatements(rules, errors, self.DM).check()
        #Recast for targets
        self.player.action = 0 #uses action
        self.DM.say(self.player.name + ' recasts call lighning', True)
        for target in targets:
            self.make_save_for(target, damage=self.recast_damge) #lets targets make saves and applies dmg
    
    def spell_dmg(self, cast_level):
        dmg = 16.5 + 5.5*(cast_level-3) #3d10 + 1d10 per lv over 3
        return dmg

    def score(self, fight, twinned_cast=False):
        #Modify super score function
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        Score = Score*(random()*2 + 1) #expecting the spell to last for 1-3 Rounds
        return Score, SpellTargets, CastLevel

#4-Level Spell

class blight(aoe_dmg_spell):
    #has aoe as super class, will be modified for single target
    def __init__(self, player):
        spell_save_type = 1 #Dex
        self.spell_name = 'Blight'
        super().__init__(player, spell_save_type, dmg_type='necrotic', aoe_area=0) #No AOE
        self.spell_text = 'blight'
        self.spell_level = 4
        self.is_range_spell = True
        self.is_twin_castable = True

    def cast(self, target, cast_level=False, twinned=False):
        if target == list: target = target[0] #mod for single cast
        super().cast(target, cast_level, twinned)

    def make_save_for(self, target, damage):
        #This function is called for every target to make the save and apply the dmg
        #It is only called once, for one target

        #calculate damage manually to account for plants
        damage = 18 + 4.5*(self.cast_level)   #upcast dmg 3d6 + 1d6 per level over 2
        extraAdvantage = 0
        if target.type == 'plant':
            extraAdvantage = -1 #disadvantage for plants
            damage = 32 + 8*self.cast_level #max dmg
            self.DM.say('is plant: ')
        save = target.make_save(self.spell_save_type,DC = self.player.spell_dc, extraAdvantage=extraAdvantage)

        if target.type == 'undead' or target.type == 'construct':
            self.DM.say('Is undead or construct and immune', True)
            self.apply_dmg(target, damage=0) #no effect on this types        
        elif save >= self.player.spell_dc:
            self.apply_dmg(target, damage=damage/2)        
        else: self.apply_dmg(target, damage=damage)
    
    def score(self, fight, twinned_cast=False):
        CastLevel = self.choose_highest_slot(4,9)
        if CastLevel == False: return self.return_0_score()

        self.addedDmg = 0  #is later added for plants, undead and constructs
        dmg = self.spell_dmg(CastLevel)
        Choices = [x for x in fight if x.team != self.player.team]
        SpellTargets = [self.player.AI.choose_att_target(Choices, AttackIsRanged=True, other_dmg = dmg, other_dmg_type=self.dmg_type, is_silent=True)]
        if SpellTargets == [False]: #No Target
            return self.return_0_score()
        if twinned_cast:
            #Secound Target for Twin Cast
            Choices.remove(SpellTargets[0]) #Do not double cast
            twin_target = self.player.AI.choose_att_target(Choices, AttackIsRanged=True, other_dmg = dmg, other_dmg_type=self.dmg_type, is_silent=True)
            if twin_target == False:
                return self.return_0_score()
            SpellTargets.append(twin_target)

        
        #DMG Score
        Score = 0
        Score += self.dmg_score(SpellTargets, CastLevel, SpellAttack=False, SpellSave=True)
        Score = Score*1.2 #good to dead focused dmg

        #Creature Type 
        for x in SpellTargets:
            if x.type == 'plant': Score += dmg/1.5
            if x.type == 'undead' or x.type == 'construct': Score -= dmg

        if twinned_cast: Score = Score*2

        Score = Score*self.random_score_scale() # a little random power 
        return Score, SpellTargets, CastLevel

    def spell_dmg(self, cast_level):
        dmg = 36 + 4.5*(cast_level-4) #8d8 + 1d8 for sl lv > 4
        return dmg
    
class sickeningRadiance(aoe_dmg_spell):
    #Not done, recheck
    def __init__(self, player):
        spell_save_type = 2 #Con
        self.spell_name = 'SickeningRadiance'
        super().__init__(player, spell_save_type, dmg_type='poison', aoe_area=2800) #No AOE
        self.spell_text = 'sickening radiance'
        self.spell_level = 4
        self.is_range_spell = True
        self.is_concentration_spell = True
        self.recast_damge = 0

    def cast(self, targets, cast_level=False, twinned=False):
        if cast_level != False: self.recast_damge = self.spell_dmg(cast_level) #set damage for later recast
        else: self.recast_damge = self.spell_dmg(self.spell_level) #level 5 spell
        #Empowered spell does not affect recast, so it checks out 
        super().cast(targets, cast_level, twinned) #Cast Spell as simple AOE once
        #Add Token for late recast
        SickeningRadianceToken(self.TM, [], cast_level) #no links

    def make_save_for(self, target, damage):
        #Modified function to account for not taking half dmg on failed save
        #This function is called for every target to make the save and apply the dmg
        save = target.make_save(self.spell_save_type,DC = self.player.spell_dc)
        if save < self.player.spell_dc:
            self.apply_dmg(target, damage=damage)

    def recast(self, targets, cast_level=False, twinned=False):
        #Recast the spell laster, if still concentrated
        rules = [self.is_known,
                 self.player.is_concentrating,]
        errors = [self.player.name + ' tried to recast ' + self.spell_name + ', without knowing the spell',
                self.player.name + ' tried to recast ' + self.spell_name + 'but is no longer concentrated']
        ifstatements(rules, errors, self.DM).check()
        #Recast for targets
        self.DM.say(self.player.name + 's sickening radiance is still on the field', True)
        for target in targets:
            self.make_save_for(target, damage=self.recast_damge) #lets targets make saves and applies dmg
    
    def spell_dmg(self, cast_level):
        dmg = 22 #4d10 no upcast improvement
        return dmg

    def score(self, fight, twinned_cast=False):
        #Modify super score function
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        Score = Score*0.75 #Reduce score, as on save no dmg
        Score = Score*(random()*2 + 1) #expecting the spell to last for 1-3 Rounds
        return Score, SpellTargets, CastLevel

class wallOfFire(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 1 #Dex
        dmg_type = 'fire'
        aoe_area = 1000 #Higher then it is, but you can shape it to hit many targets
        self.spell_name = 'WallOfFire'
        super().__init__(player, spell_save_type, dmg_type, aoe_area)
        self.spell_text = 'wall of fire'
        self.spell_level = 4
        self.is_range_spell = True
        self.is_concentration_spell = True
    
    def cast(self, targets, cast_level=False, twinned=False):
        #The wall of fire token is designed to that it will not hit the same target twice in a row
        #It will only hit 3 times
        #makes all the checks and saves and dmg
        super().cast(targets, cast_level, twinned)
        protectTarget = self
        dmg = self.spell_dmg(self.cast_level)
        #Protect yourself and one other with W.o.F.
        protectTokenSelf = WallOfFireProtectedToken(protectTarget.TM, 'wf', dmg)
        #Find another player to protect
        #self.player.AI.choose_player_to_protect(fight)
        #Problem here, cant get access to the fight list
        #Fix later
        #protectTokenOther = WallOfFireProtectedToken(protectTarget.TM, 'wf', dmg)
        spellConToken = ConcentrationToken(self.TM, [protectTokenSelf])
        self.DM.say(self.player.name + ' is protected by the wall of fire', True)

    def spell_dmg(self, cast_level):
        dmg = 22.5 + 4.5*(cast_level-4) #5d8 + 1d8/lv > 4
        return dmg
    
    def score(self, fight, twinned_cast=False):
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        Score = Score + self.spell_dmg(CastLevel)*(1.5*random()+1) #1-3 add hits while concentrated
        if self.player.knows_wild_shape: Score = Score*1.3 #good to cast before wild shape
        return Score, SpellTargets, CastLevel

class polymorph(spell):
    def __init__(self, player):
        self.spell_name = 'Polymorph'
        super().__init__(player)
        self.spell_text = 'polymorph'
        self.spell_level = 4
        self.is_range_spell = True
        self.is_concentration_spell = True
        self.is_twin_castable = True

    def cast(self, targets, cast_level=False, twinned=False):
        if type(targets) != list: targets = [targets]
        if len(targets) > 2 or len(targets) == 2 and twinned == False:
            print('Too many polymorph targets')
            quit()
        super().cast(targets, cast_level, twinned)

        #!!!!!!!!!!!!!!!!Still to do:
        ShapeName = 'TRex'
        ShapeDict = {
            'AC' : 13, 
            'HP' : 136,
            'To_Hit' : 10,
            'Type' : 'beast',
            'Attacks' : 2,
            'DMG' : 26.5,
            'Str' : 25,
            'Dex' : 10,
            'Con' : 19,
            'Int' : 2,
            'Wis' : 12,
            'Cha' : 9,
            'Damage_Type' : 'piercing',
            'Damage_Resistance' : 'none', 
            'Damage_Immunity' : 'none',
            'Damage_Vulnerabilities' : 'none'
        }

        PolymorphTokens = []
        for target in targets:
            PolymorphToken = PolymorphedToken(target.TM, subtype='pm')
            PolymorphTokens.append(PolymorphToken)
            self.DM.say(self.player.name + ' polymorphs ' + target.name + ' into ' + ShapeName, True)
            target.assume_new_shape(ShapeName, ShapeDict, Remark = 'polymorph') #make them assume new shape
            #Reshaping is handled via th ChangeCHP Function or the Concentration Token

        ConcentrationToken(self.TM, PolymorphTokens)
        #Player is now concentrated on 1-2 Polymoph Tokens

    def score(self, fight, twinned_cast=False):
        CastLevel = self.choose_smallest_slot(4,7) #Try to use low slot, higher does not make sense as polymorph does not scale
        if CastLevel == False: return self.return_0_score()

        #target must be conscious, your team and not shape changing
        potentialTargetList = [target for target in fight if target.state == 1 and target.team == self.player.team and target.is_shape_changed == False]
        if len(potentialTargetList) == 0 or (len(potentialTargetList) == 1 and twinned_cast):
            return self.return_0_score() #not enough targets
        
        SpellTargets = [self.choose_polymorph_target(potentialTargetList)]
        if twinned_cast: #choose second target
            potentialTargetList.remove(SpellTargets[0]) #remove the already choosen
            SpellTargets.append(self.choose_polymorph_target(potentialTargetList))

        Score = 0
        Score += 26.5*2*0.7*(random()*2 + 1) #dmg*2 attack + 0.7 projected hit prop. *1-3 rounds
        Score += 50*(1-self.player.CHP/self.player.HP) #add bonus for absorped damage, increases as CHP lower
        if self.player in SpellTargets: Score = Score*1.3 #prefer self to polymorph
        if twinned_cast: Score = Score*2 #twin cast
        if self.player.knows_wild_shape: Score = Score*1.2 #good to cast before wild shape

        Score = Score*self.random_score_scale()
        return Score, SpellTargets, CastLevel

    def choose_polymorph_target(self, target_list):
        scoreList = [self.polymorph_target_score(target) for target in target_list]
        #evaluate what target is the best to polymorph
        return target_list[argmax(scoreList)]

    def polymorph_target_score(self, target):
        #This Score here is not dmg euqal, becaus I did not know how to gauge it
        Score = 0
        if target.is_shape_changed: return 0
        Score += 100*(1-target.CHP/target.HP) #higher for low HP
        if target == self.player:
            if self.player.CHP < self.player.HP/3:
                Score = Score*1.5 #Cast on self preferably
        if target.heal_given > 0: Score*0.75 #rather dont polymorph healer
        return Score*self.random_score_scale()

#5-Level Spell

class cloudkill(aoe_dmg_spell):
    def __init__(self, player):
        spell_save_type = 2 #Con
        self.spell_name = 'Cloudkill'
        super().__init__(player, spell_save_type, dmg_type='poison', aoe_area=1250) #No AOE
        self.spell_text = 'cloudkill'
        self.spell_level = 5
        self.is_range_spell = True
        self.is_concentration_spell = True
        self.recast_damge = 0

    def cast(self, targets, cast_level=False, twinned=False):
        if cast_level != False: self.recast_damge = self.spell_dmg(cast_level) #set damage for later recast
        else: self.recast_damge = self.spell_dmg(self.spell_level) #level 5 spell
        #Empowered spell does not affect recast, so it checks out 
        super().cast(targets, cast_level, twinned) #Cast Spell as simple AOE once
        #Add Token for late recast
        CloudkillToken(self.TM, [], cast_level) #no links

    def recast(self, targets, cast_level=False, twinned=False):
        #Recast the spell laster, if still concentrated
        rules = [self.is_known,
                 self.player.is_concentrating,]
        errors = [self.player.name + ' tried to recast ' + self.spell_name + ', without knowing the spell',
                self.player.name + ' tried to recast ' + self.spell_name + 'but is no longer concentrated']
        ifstatements(rules, errors, self.DM).check()
        #Recast for targets
        self.DM.say(self.player.name + 's cloud kill is still on the field', True)
        for target in targets:
            self.make_save_for(target, damage=self.recast_damge) #lets targets make saves and applies dmg
    
    def spell_dmg(self, cast_level):
        dmg = 22.5 + 4.5*(cast_level-5) #5d8 + 1d8 per lv over 5
        return dmg

    def score(self, fight, twinned_cast=False):
        #Modify super score function
        Score, SpellTargets, CastLevel = super().score(fight, twinned_cast)
        Score = Score*(random()*2 + 1) #expecting the spell to last for 1-3 Rounds
        return Score, SpellTargets, CastLevel












































