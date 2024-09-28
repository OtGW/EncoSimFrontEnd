// import React, { useContext, useEffect, useState } from "react"
// import { TransferList, createStyles } from "@mantine/core"
// import { database, useAuthState } from "../../hooks/Firebase"
// import { ref, onValue } from "firebase/database"

// // const initialValues = [
// //   //heroes & monsters (unstaged)
// //   [
// //     { value: "react", label: "React", group: "Heroes" },
// //     { value: "ng", label: "Angular", group: "Enemies" },
// //     { value: "next", label: "Next.js" },
// //     { value: "blitz", label: "Blitz.js" },
// //     { value: "gatsby", label: "Gatsby.js" },
// //     { value: "vue", label: "Vue" },
// //     { value: "jq", label: "jQuery" },
// //   ],
// //   //combatants (staged)
// //   [
// //     { value: "sv", label: "Svelte" },
// //     { value: "rw", label: "Redwood" },
// //     { value: "np", label: "NumPy" },
// //     { value: "dj", label: "Django" },
// //     { value: "fl", label: "Flask" },
// //   ],
// // ]

// function CombatantsDB() {
//   const { user, data } = useAuthState()

//   const [combatantsData, setCombatantsData] = useState([[], []])

//   useEffect(() => {
//     // Check if user is authenticated and data is available
//     if (user && !data) {
//       console.log(user)
//       console.log(data)
//       console.log(database)
//       const combatantsRef = ref(database, "/Combatants")
//       const unsubscribe = onValue(combatantsRef, (snapshot) => {
//         const fetchedData = snapshot.val()
//         console.log(fetchedData)
//         if (fetchedData) {
//           const availableCombatants = Object.entries(fetchedData).map(([key, value]) => ({
//             value: value, // Store the entire combatant object as the value
//             label: value.name, // Use the name property as the label
//             group: value.Hero_or_Villain === 0 ? "Heroes" : "Enemies", // Classify into groups
//           }))
//           console.log(availableCombatants)

//           setCombatantsData([availableCombatants, []])
//         }
//       })
//       return () => unsubscribe() // Cleanup subscription
//     }
//   }, [user, data])

//   return (
//     <TransferList
//       value={combatantsData}
//       onChange={setCombatantsData}
//       searchPlaceholder={[
//         "Search combatants to add to the simulation...",
//         "Search combatants currently staged to fight...",
//       ]}
//       nothingFound={[
//         "No combatants found. Try creating your own, or load from the archive!",
//         "No combatants found...",
//       ]}
//       placeholder={[
//         "All available combatants are in the staging ground. What kind of combat are you planning, you madman?!",
//         "Heroes and monsters in this box will be included in the Simulation when you hit Run Simulator. Try adding them from the other list and they'll appear here, ready for battle!",
//       ]}
//       titles={["Available Combatants", "Staging Ground"]}
//       breakpoint="sm"
//     />
//   )
// }

// export default CombatantsDB

import React, { useEffect, useState } from "react"
import { TransferList } from "@mantine/core"
import { database, useAuthState } from "../../hooks/Firebase"
import { ref, onValue } from "firebase/database"

function CombatantsDB() {
  const { user, data } = useAuthState()

  // Separate state to hold the entire combatant objects
  const [combatantsMap, setCombatantsMap] = useState({})
  const [combatantsData, setCombatantsData] = useState([[], []])

  useEffect(() => {
    if (user && !data) {
      const combatantsRef = ref(database, "/Combatants")
      const unsubscribe = onValue(combatantsRef, (snapshot) => {
        const fetchedData = snapshot.val()
        if (fetchedData) {
          const combatantsMap = {}
          const availableCombatants = Object.entries(fetchedData).map(([key, value]) => {
            combatantsMap[key] = value
            return {
              value: key, // Use the unique key as the value
              label: value.name, // Use the name property as the label
              group: value.Hero_or_Villain === 0 ? "Heroes" : "Enemies", // Classify into groups
            }
          })

          setCombatantsMap(combatantsMap)
          setCombatantsData([availableCombatants, []])
        }
      })
      return () => unsubscribe() // Cleanup subscription
    }
  }, [user, data])

  // Function to get the selected combatants
  const getSelectedCombatants = () => {
    const selectedKeys = combatantsData[1].map((item) => item.value)
    return selectedKeys.map((key) => combatantsMap[key])
  }

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
