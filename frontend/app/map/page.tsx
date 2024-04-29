'use client'

import type { NextPage } from 'next'
import Map from '../components/Map'
import Player from '../components/Player'

const Home: NextPage = () => {
  return (
    <main className="mapContainer">
      <Map />
      <div className="playerOverlay center-bottom">
        <Player />
      </div>
    </main>
  )
}

export default Home