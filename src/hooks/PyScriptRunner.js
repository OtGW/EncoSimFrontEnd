import React, { useContext, useState } from "react"
import { PyScriptProvider, PyScript } from "pyscript-react"
import { CombatContext } from "./CombatContext"

export const usePyScriptRunner = () => {
  const { getSelectedCombatants } = useContext(CombatContext)

  const runPyScriptSimulation = (repetitions, printTurnData) => {
    const selectedCombatants = getSelectedCombatants()
    const combatantData = JSON.stringify(selectedCombatants)

    const pythonCode = `
      import json

      combatants = json.loads(${combatantData})
      repetitions = ${repetitions}
      print_turn_data = ${printTurnData}

      def simulate(combatants, repetitions, print_turn_data):
          result_summary = {}
          for i in range(repetitions):
              result = {"battle": i + 1, "combatants": combatants}
              if print_turn_data:
                  print(f"Battle {i+1}: Turn-by-turn data")
              result_summary[i] = result
          return result_summary

      result = simulate(combatants, repetitions, print_turn_data)
      print(result)
    `

    return (
      <PyScriptProvider>
        <PyScript code={pythonCode} />
      </PyScriptProvider>
    )
  }

  return { runPyScriptSimulation }
}
