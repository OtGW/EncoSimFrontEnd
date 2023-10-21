import React from "react"
import { AppShellNavbar } from "@mantine/core"
import { Burger } from "@mantine/core"
import { useDisclosure } from "@mantine/hooks"

const SideNav = () => {
  const [opened, { toggle }] = useDisclosure(false)

  return (
    <div>
      <Burger
        opened={opened}
        onClick={toggle}
        size="sm"
        aria-label="Open/Close Side Navigation"
      ></Burger>
      <AppShellNavbar
        width={300}
        style={{ height: "100%" }}
        // opened={!opened}
        // default={!opened}
        collapsed={!opened}
        // in={opened}
      />
    </div>
  )
}

export default SideNav
