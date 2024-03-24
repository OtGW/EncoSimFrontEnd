import React from "react"
import { Image } from "@mantine/core"

const Header = () => {
  return (
    <div className="head">
      <Image
        src="image dump\EncoSim logo 1.png"
        style={{ width: "150px", height: "auto", marginLeft: "30px" }}
        // style={{ fill: 1, height: "100%" }}
        // w="auto"
        // h="40"
        // pl="30"
        // fit="contain"
        alt="EncoSim logo"
        fallbackSrc="https://placehold.jp/80x80.png"
        // mantine-scale={1}
      ></Image>
    </div>
  )
}

export default Header
