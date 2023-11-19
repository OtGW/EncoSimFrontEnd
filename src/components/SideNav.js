import React from "react"
import { AppShellNavbar } from "@mantine/core"
import { Burger } from "@mantine/core"
import { useDisclosure } from "@mantine/hooks"
import { Drawer, Button } from "@mantine/core"

const SideNav = () => {
  const [opened, { open, close }] = useDisclosure(false)

  console.log("Is this working?")
  console.log("What's going on?")
  console.log("this is open state", opened)

  const navbarStyle = {
    backgroundColor: "lightblue", // Visible background color
    height: "100vh", // Full height
    display: opened ? "block" : "none", // Hide or show navbar
  }

  return (
    <>
      <Burger
        opened={opened}
        onClick={opened ? close : open}
        size="sm"
        aria-label="Open/Close Side Navigation"
        style={{ position: "absolute", zIndex: 5 }}
      />
      <Drawer
        opened={opened}
        onClose={close}
        title="Drawer"
        overlayProps={{ backgroundOpacity: 0.5, blur: 4 }}
        size="xs"
        transitionProps={{ transition: "scale-x", duration: 150, timingFunction: "linear" }}
      >
        {/* <AppShellNavbar style={navbarStyle} width={{ base: 300 }}>
          This should appear in the Drawer please
        </AppShellNavbar> */}
      </Drawer>
    </>
  )
}

export default SideNav
