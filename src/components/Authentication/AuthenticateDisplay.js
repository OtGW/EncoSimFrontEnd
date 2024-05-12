import React from "react"
import { Group, TextInput, PasswordInput, Button } from "@mantine/core"

const AuthenticateDisplay = ({ form, submitted, error }) => {
  return (
    <div>
      <Group align="center">
        <TextInput
          label="Email"
          placeholder="example@gmail.com"
          error={error}
          disabled={submitted}
          {...form.getInputProps("email")}
        />
        <PasswordInput
          label="Password"
          disabled={submitted}
          style={{ width: 200 }}
          {...form.getInputProps("password")}
        />
      </Group>
      <Button loading={submitted} type="submit">
        Submit
      </Button>
    </div>
  )
}

export default AuthenticateDisplay
