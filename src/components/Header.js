import React from "react"
import { Image } from "@mantine/core"

const Header = () => {
  return (
    <div className="head">
      <Image
        src="image dump\EncoSim logo 1.png"
        style={{ fill: 1, height: "100%" }}
        // mah={"100%"}
        // w="auto"
        fit="contain"
        alt="EncoSim logo"
        fallbackSrc="https://placehold.jp/80x80.png"
      ></Image>
    </div>
  )
}

export default Header
