import js
from js import document
from  pyodide.ffi import create_proxy
from pyodide.ffi import to_js
from os import listdir



def runSimulation(input):
    repetitions = int(Element('repetitionsInput').element.value)
    DM = DungeonMaster()
    DM.block_print()
    Hero = entity('Paladin', 0, DM, external_json=Paladin)
    Monster = entity('Barbarian', 1, DM, external_json=Barbarian)
    Fighters = [Hero, Monster]
    result = full_statistical_recap(repetitions, Fighters)
    Element('test-output').element.innerText = result

function_proxy = create_proxy(runSimulation)
document.getElementById("runAnaButton").addEventListener("click", function_proxy)

#^Definitely important




# sim_proxy = create_proxy(js_runSimulation)
# js.document.sim_proxy = sim_proxy


text = 'Simulator started...Waiting for input'
#text = str(document.getElementById("test_var").value)
#text = str(document.getElementById("test_var").innerText)
#text = str(js.test_var.to_py())
Element('test-output').element.innerText = text