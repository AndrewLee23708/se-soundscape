'use client'

import type { NextPage } from 'next'
import LoginButton from "./components/LoginButton"

const Home: NextPage = () => {
  return (
    <main>
      <div>
        <h1>Soundscapes</h1>
        <LoginButton></LoginButton>
      </div>
    </main>
  )
}

export default Home