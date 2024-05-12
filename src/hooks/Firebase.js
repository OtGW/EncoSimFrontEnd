import { getAuth, onAuthStateChanged } from "firebase/auth"
import { getDatabase, onValue, ref } from "firebase/database"
import { initializeApp } from "firebase/app"
import { useState, useEffect, useContext, createContext } from "react"

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  databaseURL: process.env.REACT_APP_FIREBASE_DATABASE_URL,
  storageBucket: process.env.REACT_APP_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID,
}
/*^For production/public Github purposes, API keys are in .env
 which is included in .gitignore*/

export const firebaseApp = initializeApp(firebaseConfig)

export const database = getDatabase(firebaseApp)

export const AuthContext = createContext()

export const AuthContextProvider = (props) => {
  const [user, setUser] = useState()
  const [error, setError] = useState()
  const [data, setData] = useState()

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(getAuth(), setUser, setError)
    return () => unsubscribe()
  }, [])

  useEffect(() => {
    const combatantsRef = ref(database, "/Combatants")

    const unsubscribe = onValue(combatantsRef, (snapshot) => {
      const databaseData = snapshot.val()
      setData(databaseData)
    })

    return () => unsubscribe()
  }, [])

  return <AuthContext.Provider value={{ user, data, error }} {...props} />
}

export const useAuthState = () => {
  const auth = useContext(AuthContext)
  return { ...auth, isAuthenticated: auth.user != null }
}
