import React from "react"
import { AppShell, Grid } from "@mantine/core"
import Header from "./Header"
import Footer from "./Footer"
import SideNav from "./SideNav"
import SimBody from "./SimBody"

const Layout = () => {
  return (
    <AppShell header={<Header />} footer={<Footer />} navbar={<SideNav />} padding="md">
      <Grid justify="center">
        <Grid.Col sm={12} md={8} lg={6} xl={6}>
          <AppShell.Header>
            <Header />
          </AppShell.Header>
          <AppShell.Navbar>
            <SideNav />
          </AppShell.Navbar>
          <AppShell.Main>
            <SimBody />
          </AppShell.Main>
          <AppShell.Footer>
            <Footer />
          </AppShell.Footer>
        </Grid.Col>
      </Grid>
    </AppShell>
  )
}

export default Layout
