'use client'

import type { NextPage } from 'next'
import { useEffect, useState } from 'react'
import { MapManager } from '../objects/MapManager'

const Home: NextPage = () => {
  useEffect(() => {
    const mapManager = new MapManager('User1', 'Profile1');
    mapManager.initMap();
  }, [])

  return (
    <main>
      <div id="map"></div>
    </main>
  )
}

export default Home
