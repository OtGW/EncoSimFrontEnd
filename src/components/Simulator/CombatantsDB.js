import React, { useEffect, useState, useContext } from "react"
import { TransferList } from "@mantine/core"
import { database, useAuthState } from "../../hooks/Firebase"
import { ref, onValue } from "firebase/database"
import { CombatContext } from "../../hooks/CombatContext"

function CombatantsDB() {
  const { user, data } = useAuthState()

  // Get context values
  const { combatantsMap, setCombatantsMap, combatantsData, setCombatantsData } =
    useContext(CombatContext)

  useEffect(() => {
    if (user && !data) {
      const combatantsRef = ref(database, "/Combatants")
      const unsubscribe = onValue(combatantsRef, (snapshot) => {
        const fetchedData = snapshot.val()
        if (fetchedData) {
          const map = {}
          const availableCombatants = Object.entries(fetchedData).map(([key, value]) => {
            map[key] = value
            return {
              value: key, // Use the unique key as the value
              label: value.name, // Use the name property as the label
              group: value.Hero_or_Villain === 0 ? "Heroes" : "Enemies", // Classify into groups
            }
          })

          setCombatantsMap(map)
          setCombatantsData([availableCombatants, []])
        }
      })
      return () => unsubscribe() // Cleanup subscription
    }
  }, [user, data, setCombatantsMap, setCombatantsData])

  return (
    <TransferList
      value={combatantsData}
      onChange={setCombatantsData}
      searchPlaceholder={[
        "Search combatants to add to the simulation...",
        "Search combatants currently staged to fight...",
      ]}
      nothingFound={[
        "No combatants found. Try creating your own, or load from the archive!",
        "No combatants found...",
      ]}
      placeholder={[
        "All available combatants are in the staging ground. What kind of combat are you planning, you madman?!",
        "Heroes and monsters in this box will be included in the Simulation when you hit Run Simulator. Try adding them from the other list and they'll appear here, ready for battle!",
      ]}
      titles={["Available Combatants", "Staging Ground"]}
      breakpoint="sm"
    />
  )
}

export default CombatantsDB
