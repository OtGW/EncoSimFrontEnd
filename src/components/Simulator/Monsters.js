import React from "react"
import { Button } from "@mantine/core"

const Monsters = () => {
  return (
    <>
      <Button
        variant="filled"
        color="brand" // Use the 'brand' color from the custom theme
        // other props
      >
        Monster button
      </Button>
      <Button
        variant="filled"
        color="brand" // Use the 'brand' color from the custom theme
        // other props
      >
        +
      </Button>
    </>
  )
}

export default Monsters
