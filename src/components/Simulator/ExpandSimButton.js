import React from "react"
import SimParams from "./SimParams"
import { Button, Affix, rem, Transition } from "@mantine/core"
import { useDisclosure } from "@mantine/hooks"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import { faHatWizard } from "@fortawesome/free-solid-svg-icons"

const ExpandSimButton = () => {
  const [opened, handler] = useDisclosure(false)

  return (
    <div
    //   style={{
    //     maxWidth: rem(200),
    //     position: "relative",
    //     display: "flex",
    //     justifyContent: "center",
    //     margin: "auto",
    //   }}
    >
      <Affix position={{ bottom: rem(20), right: rem(20) }}>
        <Button
          onClick={() => handler.toggle()}
          rightIcon={<FontAwesomeIcon icon={faHatWizard} size="xl" />}
        >
          {opened ? "Hide Sim" : "Open Sim"}
        </Button>
      </Affix>

      <Transition mounted={opened} transition="fade" duration={400} timingFunction="ease">
        {(styles) => <SimParams style={styles} />}
        {/* <SimParams opened={opened} /> */}
      </Transition>
      {/* {SimParams} */}
    </div>
  )
}

export default ExpandSimButton
