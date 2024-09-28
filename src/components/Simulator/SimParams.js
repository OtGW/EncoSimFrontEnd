import React from "react"
import { useState, useRef } from "react"
import { Button, NumberInput, createStyles, Flex, Container, Tooltip } from "@mantine/core"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import {
  faDiceD20,
  faDice,
  faDungeon,
  faHandFist,
  faScroll,
} from "@fortawesome/free-solid-svg-icons"
import NewCombatantModal from "./NewCombatantModal"
import { usePyScriptRunner } from "../../hooks/PyScriptRunner"

const useStyles = createStyles((theme) => ({
  button: {
    backgroundColor: theme.colors.blue[6],
    color: theme.white,
    padding: "10px 20px",
    "&:hover": {
      backgroundColor: theme.colors.blue[7],
    },
    "&.selected": {
      backgroundColor: theme.white, // Inverted background color
      color: theme.colors.blue[6], // Inverted text color
      borderColor: theme.colors.blue[6], // Optional: if using borders
    },
  },
}))

const SimParams = ({ styles }) => {
  const { classes } = useStyles()
  const [repetitions, setRepetitions] = useState("")
  const ref = useRef(null)
  const [printTurnData, setPrintTurnData] = useState(false)
  const [newCharOpened, setNewCharOpened] = useState(false)

  const { runPyScriptSimulation } = usePyScriptRunner() // Use custom hook to get the simulation function

  const runSimulation = () => {
    // Call the PyScriptRunner with repetitions and printTurnData
    runPyScriptSimulation(repetitions, printTurnData)
  }

  return (
    <div style={{ styles }}>
      <Flex mt="xs" gap="md" justify="center" align="center" direction="row" wrap="wrap">
        <Tooltip
          withArrow
          label="Feel free to play around! Save your changes for next time by logging in.">
          <Button
            className={classes.button}
            leftIcon={<FontAwesomeIcon icon={faHandFist} size="xl" />}
            onClick={() => setNewCharOpened(true)}>
            New Combatant
          </Button>
        </Tooltip>
        <Tooltip withArrow label="Recommended for advanced users only">
          <Button
            className={classes.button}
            leftIcon={<FontAwesomeIcon icon={faDiceD20} size="xl" />}>
            DM Mode
          </Button>
        </Tooltip>
        <Tooltip
          withArrow
          label="Adds a random selection of heroes and enemies to the staging ground, then runs the simulator.">
          <Button className={classes.button} leftIcon={<FontAwesomeIcon icon={faDice} size="xl" />}>
            Try Me! [Randomize]
          </Button>
        </Tooltip>
      </Flex>
      <Container>
        <NumberInput
          type="text"
          placeholder="Input # of Simulator Repetitions"
          label="Repetitions:"
          withAsterisk
          value={repetitions}
          onChange={(event) => setRepetitions(event.currentTarget.value)} //this might need to be currentTarget.repetitions
          ref={ref}
        />
      </Container>

      <Flex mt="xs" gap="md" justify="center" align="center" direction="row" wrap="wrap">
        <Tooltip
          position="bottom"
          withArrow
          multiline
          width={220}
          label="Roll for initiative! Heroes and enemies in the staging ground will do battle until one
           side is completely defeated, a number of times equal to the repetitions 
           entered above. A summary screen will then display the results averaged 
           across each battle, including metrics on each combatant's performance 
           and insights on encounter difficulty, to help you balance (or unbalance - do you) your encounters at 
           the table. This simulation uses the official rules of your chosen turn-based tabletop game.">
          <Button
            onClick={runSimulation}
            className={classes.button}
            leftIcon={<FontAwesomeIcon icon={faDungeon} size="xl" />}>
            Run Simulator
          </Button>
        </Tooltip>
        <Tooltip
          position="bottom"
          withArrow
          label="Warning: if you set more than a few repetitions this file will be extremely long!">
          <Button
            onClick={() => setPrintTurnData((print) => !print)}
            className={`${classes.button} ${printTurnData ? "selected" : ""}`}
            leftIcon={<FontAwesomeIcon icon={faScroll} size="xl" />}>
            Print Turn-By-Turn Data
          </Button>
        </Tooltip>
      </Flex>
      <NewCombatantModal opened={newCharOpened} setOpened={setNewCharOpened} />
    </div>
  )
}

export default SimParams
