import js
from js import document
from  pyodide.ffi import create_proxy
from pyodide.ffi import to_js
from os import listdir

Barbarian = {
    "AC": 16,
    "HP": 55,
    "Proficiency": 3,
    "To_Hit": 7.0,
    "Attacks": 2.0,
    "DMG": 10.5,
    "Level": 5.0,
    "Str": 18,
    "Dex": 13,
    "Con": 16,
    "Int": 8,
    "Wis": 11,
    "Cha": 12,
    "Saves_Proficiency": "Str Con ",
    "Hero_or_Villain": 0,
    "Damage_Type": "slashing",
    "Damage_Resistance": "none",
    "Damage_Immunity": "none",
    "Damage_Vulnerabilities": "none",
    "Spell_DC": 10,
    "Spell_Mod": 0,
    "Spell_Slot_1": 0,
    "Spell_Slot_2": 0,
    "Spell_Slot_3": 0,
    "Spell_Slot_4": 0,
    "Spell_Slot_5": 0,
    "Spell_Slot_6": 0,
    "Spell_Slot_7": 0,
    "Spell_Slot_8": 0,
    "Spell_Slot_9": 0,
    "Spell_List": "none",
    "Other_Abilities": "Rage RecklessAttack Frenzy ",
    "Sneak_Attack_Dmg": 0.0,
    "Lay_on_Hands_Pool": 0,
    "Sorcery_Points": 0,
    "Position": "front",
    "Speed": 30,
    "Range_Attack": 0,
    "DruidCR": 0.0,
    "OffHand": 0.0,
    "Type": "normal",
    "Inspiration": "0",
    "DestroyUndeadCR": 0.0,
    "ChannelDivinity": 0,
    "ActionSurges": 0,
    "RageDmg": 2.0
}

Paladin = {
    "AC": 21,
    "HP": 44,
    "Proficiency": 3,
    "To_Hit": 7.0,
    "Attacks": 2.0,
    "DMG": 11.0,
    "Level": 5.0,
    "Str": 16,
    "Dex": 14,
    "Con": 14,
    "Int": 9,
    "Wis": 11,
    "Cha": 16,
    "Saves_Proficiency": "Wis Cha ",
    "Hero_or_Villain": 0,
    "Damage_Type": "slashing",
    "Damage_Resistance": "none",
    "Damage_Immunity": "none",
    "Damage_Vulnerabilities": "none",
    "Spell_DC": 14,
    "Spell_Mod": 3,
    "Spell_Slot_1": 4,
    "Spell_Slot_2": 2,
    "Spell_Slot_3": 0,
    "Spell_Slot_4": 0,
    "Spell_Slot_5": 0,
    "Spell_Slot_6": 0,
    "Spell_Slot_7": 0,
    "Spell_Slot_8": 0,
    "Spell_Slot_9": 0,
    "Spell_List": "CureWounds SpiritualWeapon ",
    "Other_Abilities": "Interception Smite ",
    "Sneak_Attack_Dmg": 0.0,
    "Lay_on_Hands_Pool": 25,
    "Sorcery_Points": 0,
    "Position": "front",
    "Speed": 30,
    "Range_Attack": 0,
    "DruidCR": 0.0,
    "OffHand": 0.0,
    "Type": "normal",
    "Inspiration": 0,
    "DestroyUndeadCR": 0.0,
    "ChannelDivinity": 0,
    "ActionSurges": 0,
    "RageDmg": 0.0,
    "AOERechargeDmg": 0.0,
    "AOERechargeDC": 0,
    "AOESaveType": 0,
    "AOERechargeArea": 0,
    "AOERechargePropability": 0.0,
    "AOERechargeType": "fire",
    "StartOfTurnHeal": 0,
    "LegendaryResistances": 0,
    "FavoredFoeDmg": 0.0,
    "StrategyLevel": 5
}


repetitions = 100
DM = DungeonMaster()
DM.block_print()
Hero = entity('Paladin', 0, DM, external_json=Paladin)
Monster = entity('Barbarian', 1, DM, external_json=Barbarian)
Fighters = [Hero, Monster]
result = full_statistical_recap(repetitions, Fighters)
print(result)

# def runSimulation(repetitions):
#     DM = DungeonMaster()
#     DM.block_print()
#     Hero = entity('Paladin', 0, DM, external_json=Paladin)
#     Monster = entity('Barbarian', 1, DM, external_json=Barbarian)
#     Fighters = [Hero, Monster]
#     result = full_statistical_recap(repetitions, Fighters)
#     print(result)


# def runSimulation(input):
#     repetitions = int(Element('repetitionsInput').element.value)
#     DM = DungeonMaster()
#     DM.block_print()
#     Hero = entity('Paladin', 0, DM, external_json=Paladin)
#     Monster = entity('Barbarian', 1, DM, external_json=Barbarian)
#     Fighters = [Hero, Monster]
#     result = full_statistical_recap(repetitions, Fighters)
#     Element('test-output').element.innerText = result

# function_proxy = create_proxy(runSimulation)
# document.getElementById("runAnaButton").addEventListener("click", function_proxy)

# text = 'Simulator started...Waiting for input'
# Element('test-output').element.innerText = text