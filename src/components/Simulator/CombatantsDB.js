import React, { useContext, useEffect, useState } from "react"
import { TransferList, createStyles } from "@mantine/core"
// import { AuthContext } from "../../hooks/Firebase"
import { database, useAuthState } from "../../hooks/Firebase"
import { ref, onValue } from "firebase/database"

// const initialValues = [
//   //heroes & monsters (unstaged)
//   [
//     { value: "react", label: "React", group: "Heroes" },
//     { value: "ng", label: "Angular", group: "Enemies" },
//     { value: "next", label: "Next.js" },
//     { value: "blitz", label: "Blitz.js" },
//     { value: "gatsby", label: "Gatsby.js" },
//     { value: "vue", label: "Vue" },
//     { value: "jq", label: "jQuery" },
//   ],
//   //combatants (staged)
//   [
//     { value: "sv", label: "Svelte" },
//     { value: "rw", label: "Redwood" },
//     { value: "np", label: "NumPy" },
//     { value: "dj", label: "Django" },
//     { value: "fl", label: "Flask" },
//   ],
// ]

// const useStyles = createStyles((theme) => ({
//   item: {
//     height: "30px", // Reduce height of each item
//     lineHeight: "30px", // Adjust line height to align text vertically
//     fontSize: theme.fontSizes.sm, // Adjust font size accordingly
//   },
//   customListStyle: {
//     "& .mantine-TransferList-list": {
//       maxHeight: "400px",
//       overflowY: "auto",
//     },
//   },
// }))

function Combatants() {
  // const { classes } = useStyles()
  const { user, data } = useAuthState()

  // const { data } = useContext(AuthContext)

  const [combatantsData, setCombatantsData] = useState([[], []])

  // useEffect(() => {
  //   if (data && data.Combatants) {
  //     const availableCombatants = Object.entries(data.Combatants).map(([key, value]) => ({
  //       value: value, // Pass the whole combatant object as the value
  //       label: key, // Use the key as the label
  //       group: value.Hero_or_Villain === 0 ? "Heroes" : "Enemies", // Assuming there is a Hero_or_Villain property to distinguish groups
  //     }))
  //     setCombatantsData([availableCombatants, []]) // Sets available combatants in the first list, second list initially empty
  //     console.log("Processed combatants data:", availableCombatants)
  //   }
  // }, [data])

  useEffect(() => {
    // Check if user is authenticated and data is available
    if (user && !data) {
      console.log(user)
      console.log(data)
      console.log(database)
      const combatantsRef = ref(database, "/Combatants")
      const unsubscribe = onValue(combatantsRef, (snapshot) => {
        const fetchedData = snapshot.val()
        console.log(fetchedData)
        if (fetchedData) {
          const availableCombatants = Object.entries(fetchedData).map(([key, value]) => ({
            value: value, // Store the entire combatant object as the value
            label: value.name, // Use the name property as the label
            group: value.Hero_or_Villain === 0 ? "Heroes" : "Enemies", // Classify into groups
          }))
          console.log(availableCombatants)

          setCombatantsData([availableCombatants, []])
        }
      })
      return () => unsubscribe() // Cleanup subscription
    }
  }, [user, data])

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
      // classNames={{ body: classes.customListStyle }}
      // itemComponent={({ data }) => <div className={classes.item}>{data.label}</div>}
    />
  )
}

export default Combatants
