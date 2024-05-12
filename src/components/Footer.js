import React from "react"
import { Container, Group, ActionIcon, rem, Image, createStyles } from "@mantine/core"
// import { IconBrandTwitter, IconBrandYoutube, IconBrandInstagram } from "@tabler/icons-react"
// import { MantineLogo } from "@mantinex/mantine-logo"
import { FontAwesomeIcon } from "@fortawesome/react-fontawesome"
import {
  faTwitter,
  faYoutube,
  faInstagram,
  faDAndD,
  faDiscord,
} from "@fortawesome/free-brands-svg-icons"
// import classes from "./Footer.module.css"

const useStyles = createStyles((theme) => ({
  footer: {
    marginTop: theme.spacing.xl * 3,
    borderTop: `1px solid ${
      theme.colorScheme === "dark" ? theme.colors.dark[5] : theme.colors.gray[2]
    }`,
    backgroundColor: "#ffffff",
    color: theme.colorScheme === "dark" ? theme.colors.gray[0] : theme.colors.dark[7], // Adjust text color based on theme
    height: "auto",
  },
  inner: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    // paddingTop: theme.spacing.xl,
    // paddingBottom: theme.spacing.xl,

    // Responsive adjustments
    [`@media (max-width: ${theme.breakpoints.xs}px)`]: {
      flexDirection: "column",
    },
  },
  links: {
    [`@media (max-width: ${theme.breakpoints.xs}px)`]: {
      marginTop: theme.spacing.md,
    },
  },
}))

function Footer() {
  const { classes } = useStyles()

  return (
    <div className={classes.footer}>
      <Container className={classes.inner}>
        <Image
          src="image dump\EncoSim text only 2.png"
          alt="EncoSim logo"
          fallbackSrc="https://placehold.jp/80x80.png"
          style={{ width: "70px", height: "auto" }}
        />
        <Group gap={0} className={classes.links} justify="flex-end" wrap="wrap">
          <ActionIcon size="lg" color="gray" variant="subtle">
            <FontAwesomeIcon icon={faTwitter} style={{ fontSize: "18px" }} />
          </ActionIcon>
          <ActionIcon size="lg" color="gray" variant="subtle">
            <FontAwesomeIcon icon={faYoutube} style={{ fontSize: "18px" }} />
          </ActionIcon>
          <ActionIcon size="lg" color="gray" variant="subtle">
            <FontAwesomeIcon icon={faInstagram} style={{ fontSize: "18px" }} />
          </ActionIcon>
          <ActionIcon size="lg" color="gray" variant="subtle">
            <FontAwesomeIcon icon={faDAndD} />
          </ActionIcon>
          <ActionIcon size="lg" color="gray" variant="subtle">
            <FontAwesomeIcon icon={faDiscord} />
          </ActionIcon>
        </Group>
      </Container>
    </div>
  )
}

export default Footer
