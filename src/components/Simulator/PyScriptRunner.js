// src/components/PyScriptComponent.js
import React from "react"

const PyScriptComponent = () => {
  return (
    <py-script src="Simulator.py">
      {/* The combatant data and variables will be injected here from the CombatForm */}
    </py-script>
  )
}

export default PyScriptComponent
