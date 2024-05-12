import React from "react"
import { Image, BackgroundImage, createStyles, Group } from "@mantine/core"
import Authenticate from "./Authentication/Authenticate"

const useStyles = createStyles((theme) => ({
  header: {
    backgroundColor: "#29333d",
    borderBottom: `3px solid ${theme.colors.yellow[4]}`, // Gold trim using Mantine theme
    color: theme.white,
    padding: "10px 20px",
  },
}))

const Header = () => {
  const { classes } = useStyles()

  return (
    <div className={classes.header}>
      {/* <BackgroundImage src="/image dump/wood-grain.jpg" style={{ height: "100%" }}> */}
      <Group position="apart">
        <Image
          src="image dump\EncoSim logo 1.png"
          style={{ width: "100px", height: "auto", marginLeft: "30px" }}
          // style={{ fill: 1, height: "100%" }}
          // w="auto"
          // h="40"
          // pl="30"
          // fit="contain"
          alt="EncoSim logo"
          fallbackSrc="https://placehold.jp/80x80.png"
          // mantine-scale={1}
        />
        <Authenticate />
      </Group>

      {/* </BackgroundImage> */}
    </div>
  )
}

export default Header

// <div className="head">
