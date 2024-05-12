import React from "react"
import { useDisclosure } from "@mantine/hooks"
import { Drawer, BackgroundImage, Burger, List, createStyles } from "@mantine/core"

const useStyles = createStyles((theme) => ({
  drawerContent: {
    backgroundImage: 'url("/image dump/wood-grain.jpg")',
    backgroundSize: "cover",
    height: "100%", // Ensure the image covers the whole Drawer.Body
    padding: theme.spacing.md,
  },
}))

const SideNav = () => {
  const [opened, { open, close }] = useDisclosure(false)
  const { classes } = useStyles()

  console.log("Is this working?")
  console.log("What's going on?")
  console.log("this is open state", opened)

  return (
    <>
      <Burger
        opened={opened}
        onClick={opened ? close : open}
        size="sm"
        aria-label="Open/Close Side Navigation"
        style={{ position: "absolute", zIndex: 5 }}
      />
      {/* <div className={classes.navbar}> */}
      <Drawer.Root
        opened={opened}
        onClose={close}
        // title="Drawer"
        overlayProps={{ backgroundOpacity: 0.5, blur: 4 }}
        size="xs"
        transitionProps={{ transition: "scale-x", duration: 150, timingFunction: "linear" }}
        closeButtonProps={{ "aria-label": "Close modal" }}
      >
        <Drawer.Overlay />
        <Drawer.Content className={classes.drawerContent}>
          <Drawer.Header>
            <Drawer.Title>Title</Drawer.Title>
            <Drawer.CloseButton />
          </Drawer.Header>
          <Drawer.Body>
            {/* <BackgroundImage src="/image dump/wood-grain.jpg"> */}
            <List>
              <List.Item>Tutorial</List.Item>
              <List.Item>About</List.Item>
              <List.Item>Links</List.Item>
              <List.Item>Go Premium</List.Item>
              <List.Item>Tip Jar</List.Item>
            </List>
          </Drawer.Body>

          {/* </BackgroundImage> */}
        </Drawer.Content>
      </Drawer.Root>
      {/* </div> */}
    </>
  )
}

export default SideNav
