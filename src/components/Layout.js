import React from "react"
import { AppShell, Grid, useMantineTheme, BackgroundImage } from "@mantine/core"
import Header from "./Header"
import Footer from "./Footer"
import SideNav from "./SideNav"
import SimBody from "./SimBody"

const Layout = () => {
  const theme = useMantineTheme()

  return (
    <BackgroundImage src="/image dump/Background.jpg" radius="sm">
      <AppShell padding="md" header={<Header />} footer={<Footer />} navbar={<SideNav />}>
        <Grid justify="center">
          <Grid.Col sm={12} md={8} lg={6} xl={6}>
            <SimBody />
          </Grid.Col>
        </Grid>
      </AppShell>
    </BackgroundImage>
  )
}

export default Layout
