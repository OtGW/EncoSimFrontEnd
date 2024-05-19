import React from "react"
import Heroes from "./Simulator/Heroes"
import Monsters from "./Simulator/Monsters"
import SimOutput from "./Simulator/SimOutput"
import SimParams from "./Simulator/SimParams"
import ExpandSimButton from "./Simulator/ExpandSimButton"
// import Combatants from "./Simulator/Combatants"
import CombatantsDB from "./Simulator/CombatantsDB"
import {
  createStyles,
  Container,
  Grid,
  Col,
  Text,
  Stack,
  Title,
  Space,
  Center,
} from "@mantine/core"

const useStyles = createStyles((theme) => ({
  section: {
    backgroundColor: theme.colors.gray[0], // Light background color
    padding: theme.spacing.md,
    borderRadius: theme.radius.md,
    boxShadow: theme.shadows.sm,
  },
}))

const SimBody = () => {
  const { classes } = useStyles()
  return (
    <Center className={classes.section}>
      <Stack spacing="xl" justify="space-around">
        <Title>Combatants:</Title>
        {/* <Combatants /> */}
        <CombatantsDB />
        <Space h="md" />
        {/* <Heroes />
      <Monsters /> */}
        <ExpandSimButton />
        <SimOutput />
        {/* <SimParams />*/}
      </Stack>
    </Center>
  )
}

export default SimBody
