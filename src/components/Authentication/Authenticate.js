import React, { useState } from "react"
import { useAuthState } from "../../hooks/Firebase"
import { Button } from "@mantine/core"
import { useForm } from "@mantine/form"
import AuthenticateDisplay from "./AuthenticateDisplay.js"
import {
  fetchSignInMethodsForEmail,
  getAuth,
  createUserWithEmailAndPassword,
  signInWithEmailAndPassword,
  signOut,
} from "firebase/auth"

const Authenticate = () => {
  const { user, isAuthenticated } = useAuthState()
  const [error, setError] = useState("")
  const [submitted, setSubmitted] = useState(false)
  const auth = getAuth()
  const form = useForm({
    initialValues: {
      email: "",
      password: "",
    },
    validate: {
      email: (value) => (/^\S+@\S+$/.test(value) ? null : "Invalid email"),
    },
  })

  // const submitForm = async (values) => {
  //   setSubmitted(true)
  //   fetchSignInMethodsForEmail(auth, values.email)
  //     .then(async (methods) => {
  //       if (methods.length > 0) {
  //         // If the email is already used for signing up (e.g., password method exists)
  //         if (methods.includes("password")) {
  //           try {
  //             const userCredential = await signInWithEmailAndPassword(
  //               auth,
  //               values.email,
  //               values.password
  //             )
  //             setSubmitted(false)
  //             // Handle successful sign-in here (if needed)
  //           } catch (err) {
  //             setSubmitted(false)
  //             // More specific error handling based on the error code
  //             if (err.code === "auth/wrong-password") {
  //               setError("Incorrect password. Please try again.")
  //             } else {
  //               setError("Login failed. Please try again.")
  //             }
  //           }
  //         } else {
  //           // Handle other methods or inform user about the available methods
  //           setError(
  //             "This email is registered but not with a password. Did you use a different sign-in method?"
  //           )
  //           setSubmitted(false)
  //         }
  //       } else {
  //         // No user is registered with this email, create a new account
  //         try {
  //           const newUser = await createUserWithEmailAndPassword(
  //             auth,
  //             values.email,
  //             values.password
  //           )
  //           setSubmitted(false)
  //           // Handle new user creation here (if needed)
  //         } catch (err) {
  //           setSubmitted(false)
  //           setError(err.message) // Optionally, refine these messages too
  //         }
  //       }
  //     })
  //     .catch((error) => {
  //       setSubmitted(false)
  //       setError("Failed to check existing sign-in methods. Please try again.")
  //     })
  // }

  const submitForm = async (values) => {
    setSubmitted(true)
    fetchSignInMethodsForEmail(auth, values.email).then(async (value) => {
      if (value.length >= 1) {
        await signInWithEmailAndPassword(auth, values.email, values.password)
          .then((userCredential) => {
            setSubmitted(false)
          })
          .catch((err) => {
            setSubmitted(false)
            setError(err.message)
          })
      } else {
        await createUserWithEmailAndPassword(auth, values.email, values.password)
          .then((data) => {
            setSubmitted(false)
          })
          .catch((err) => {
            console.log(err.message)
            setSubmitted(false)
            setError(err.message)
          })
      }
    })
  }

  if (!isAuthenticated) {
    return (
      <div>
        <form onSubmit={form.onSubmit((values) => submitForm(values))}>
          <AuthenticateDisplay form={form} submitted={submitted} error={error} />
        </form>
      </div>
    )
  } else {
    console.log(user)
    return (
      <div>
        <h1>
          Thank you for logging in, {user?.email}, combatants you create will be saved to your
          profile.
        </h1>
        <Button onClick={() => signOut(auth)}>Logout</Button>
      </div>
    )
  }
}

export default Authenticate
