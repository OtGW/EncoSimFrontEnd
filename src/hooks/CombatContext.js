import React, { createContext, useState } from "react"

// Create the context
export const CombatContext = createContext()

// Context provider component
export const CombatProvider = ({ children }) => {
  const [combatantsMap, setCombatantsMap] = useState({})
  const [combatantsData, setCombatantsData] = useState([[], []])

  // Function to get selected combatants
  const getSelectedCombatants = () => {
    const selectedKeys = combatantsData[1].map((item) => item.value)
    return selectedKeys.map((key) => combatantsMap[key])
  }

  return (
    <CombatContext.Provider
      value={{
        combatantsMap,
        setCombatantsMap,
        combatantsData,
        setCombatantsData,
        getSelectedCombatants,
      }}>
      {children}
    </CombatContext.Provider>
  )
}
