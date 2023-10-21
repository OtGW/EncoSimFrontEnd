import "./App.css"
import React, { useState } from "react"
import "@mantine/core/styles.css"
import { MantineProvider } from "@mantine/core"
import Layout from "./components/Layout"

function App() {
  return (
    <MantineProvider>
      <Layout />
    </MantineProvider>
  )
}

export default App
