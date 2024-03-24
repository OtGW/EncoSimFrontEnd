import React from "react"
import Heroes from "./Simulator/Heroes"
import Monsters from "./Simulator/Monsters"
import SimOutput from "./Simulator/SimOutput"
import SimParams from "./Simulator/SimParams"

const SimBody = () => {
  return (
    <>
      <h1>SimBody content</h1>
      <Heroes />
      <Monsters />
      <SimOutput />
      <SimParams />
    </>
  )
}

export default SimBody
