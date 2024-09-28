import "./App.css"
import React, { useState } from "react"
import { MantineProvider } from "@mantine/core"
import Layout from "./components/Layout"
import { AuthContextProvider } from "./hooks/Firebase"
import { CombatProvider } from "./hooks/CombatContext"

function App() {
  return (
    <CombatProvider>
      <MantineProvider
        theme={{
          colorScheme: "light",
          fontFamily: "Garamond, serif", // Example of a font that might fit the theme
          colors: {
            brown: ["#7f6e5d", "#9f8d7c", "#bfaa9b", "#dfcaba", "#fff9f8"], // Define shades of brown
          },
          primaryColor: "brown", // Use the key of the newly defined color
          spacing: { md: 20 },
          shadows: { sm: "0 1px 3px rgba(0,0,0,0.1)" },
          radius: { md: 4 },

          components: {
            Button: {
              styles: (theme) => ({
                root: {
                  backgroundColor: theme.colors.brown[0], // Use the darkest shade of brown for button background
                  color: theme.white, // Ensure text is white for contrast
                  "&:hover": {
                    backgroundColor: theme.colors.brown[1], // Lighter brown on hover
                  },
                },
              }),
            },
          },
        }}
        withGlobalStyles
        withNormalizeCSS>
        <AuthContextProvider>
          <Layout />
        </AuthContextProvider>
      </MantineProvider>
    </CombatProvider>
  )
}

export default App
