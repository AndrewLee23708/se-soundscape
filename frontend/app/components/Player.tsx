'use client'
import React, { useState, useEffect } from 'react'

let url = 'https://sdk.scdn.co/spotify-player.js'

export default function Player() {
  const [isPlaying, setIsPlaying] = useState(false)

  useEffect(() => {
    async function init() {
      const token = loadToken()
      const player = await initPlayer(token)
      await initPlayback(token, player)
      setListeners(player)
    }

    init()
  }, [])

  return (
    <div className="button-container">
      <button id="previous" className="spaced-button">
        <img src="/prev.png" alt="Previous" />
      </button>
      <button id="toggle" className="spaced-button">
        <img
          src={isPlaying ? '/pause.png' : '/play.png'}
          alt={isPlaying ? 'Pause' : 'Play'}
        />
      </button>
      <button id="skip" className="spaced-button">
        <img src="/skip.png" alt="Skip" />
      </button>
    </div>
  )
}

/**
 * @description Fetches Spotify access token from query params
 * @returns {string} Returns Spotify access token
 */
function loadToken() {
  const urlParams = new URLSearchParams(window.location.search)
  return urlParams.get('token')
}

/**
 * @description Initializes Spotify player
 * @param {string} token - Spotify access token
 * @description Loads Spotify Web Player SDK script into client. Upon successful load, instantiates a new Spotify Web Player instance.
 * @returns {Promise<any>} Returns promise containing newly instantiated Spotify player instance
 */
async function initPlayer(token: any) {
  return new Promise((resolve, reject) => {
    const script = document.createElement('script')
    script.src = 'https://sdk.scdn.co/spotify-player.js'
    script.async = true
    document.body.appendChild(script)

    window.onSpotifyWebPlaybackSDKReady = () => {
      const player = new Spotify.Player({
        name: 'Soundscapes',
        getOAuthToken: (cb) => cb(token),
        volume: 0.5,
      })
      resolve(player)
    }
  })
}

/**
 * @description Initializes Spotify web playback
 * @param {string} token - Spotify access token
 * @param {player} player - Reference to Spotify Web Player instance
 * @description Connects Spotify Web Player instance. Upon successful connection, stores access token and corresponding device id for later use. Also stores user id.
 * @returns {void} Returns nothing
 */
async function initPlayback(token: any, player: any) {
  await fetchUser(token)
  player.connect()
  player.addListener('ready', async ({ device_id }) => {
    localStorage.setItem('token', token)
    localStorage.setItem('device_id', device_id)
  })
}

/**
 * @description Stores Spotify user id in local storage
 * @param {string} token - Spotify access token
 * @description Fetches Spotify user id and stores it in local storage
 * @returns {void} Returns nothing
 */
async function fetchUser(token: any) {
  const response = await fetch('http://127.0.0.1:5000/user', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      token: token,
    }),
  })
  const data = await response.json()
  const user_id = data.display_name
  localStorage.setItem('user_id', user_id)
}

/**
 * @description Sets event listeners for Web Playback UI
 * @param {player} player - Reference to Spotify Web Player instance
 * @description Sets event listener functions for Web Player such as toggling playback, skipping, previous track, and disconnecting before unload
 * @returns {void} Returns nothing
 */
function setListeners(player: any) {
  document.getElementById('toggle').onclick = function () {
    player.togglePlay()
  }
  document.getElementById('skip').onclick = function () {
    player.nextTrack()
  }
  document.getElementById('previous').onclick = function () {
    player.previousTrack()
  }
  window.addEventListener('beforeunload', function (event) {
    player.disconnect()
  })
}
