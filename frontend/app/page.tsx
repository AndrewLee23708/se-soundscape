'use client'

import type { NextPage } from 'next'
import LoginButton from "./components/LoginButton"

const Home: NextPage = () => {
  return (
    <main>
      <div className="container-fluid center-vertically">
        <h1 style={{ fontSize: "6vw" }}>Soundscapes</h1>
        <p style={{ fontSize: "1.5vw" }}>What does your world sound like?</p>
        <LoginButton></LoginButton>
      </div>
    </main>
  )
}

export default Home