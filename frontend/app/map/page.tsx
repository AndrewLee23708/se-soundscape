'use client'

import type { NextPage } from 'next'
import Map from '../components/Map'
import Player from '../components/Player'

const Home: NextPage = () => {
  return (
    <main>
      <Map></Map>
      <Player></Player>
    </main>
  )
}

export default Home