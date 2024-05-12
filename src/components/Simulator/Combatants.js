import React from "react"
import { useState, useEffect } from "react"
import { TransferList, createStyles } from "@mantine/core"

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

  const [data, setData] = useState([[], []])

  useEffect(() => {
    // Define an async function to load and process data
    const loadData = async () => {
      try {
        // Fetch the list of filenames from the public directory
        const response = await fetch("/combatantsFilenames.json")
        const filenames = await response.json()

        // Fetch each entity JSON file and process it
        const items = await Promise.all(
          filenames.map(async (filename) => {
            const response = await fetch(`/Entities/${filename}`)
            const entity = await response.json()
            return {
              value: entity, // Store the entire entity object
              label: filename.replace(".json", ""), // Use the filename as label, minus the extension
              group: entity.Hero_or_Villain === 0 ? "Heroes" : "Enemies",
            }
          })
        )

        // All items initially go into the first array; second array starts empty
        setData([items, []])
      } catch (error) {
        console.error("Error loading filenames:", error)
      }
    }

    loadData() // Call the async function within useEffect
  }, [])

  return (
    <TransferList
      value={data}
      onChange={setData}
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
