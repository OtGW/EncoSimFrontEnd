import React from "react"
import { AppShell, Burger, Grid } from "@mantine/core"
import { useDisclosure } from "@mantine/hooks"
import Header from "./Header"
import Footer from "./Footer"
import SideNav from "./SideNav"
import SimBody from "./SimBody"
// import "./Styles.css"

const Layout = ({ state }) => {
  const [opened, { toggle }] = useDisclosure()

  return (
    <AppShell header={<Header />} footer={<Footer />} navbar={<SideNav />}>
      <Grid justify="center">
        <Grid.Col sm={12} md={8} lg={6} xl={6}>
          <SimBody />
        </Grid.Col>
      </Grid>
    </AppShell>
  )
}

export default Layout
