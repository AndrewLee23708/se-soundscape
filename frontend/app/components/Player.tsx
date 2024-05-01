'use client'
import React, { useState, useEffect, useRef } from 'react'

let url = 'https://sdk.scdn.co/spotify-player.js'

export default function Player({ isPlayback }) {
  const [userId, setUserId] = useState('')
  const [isPlaying, setIsPlaying] = useState(false)
  const [songName, setSongName] = useState('')
  const [songArtist, setSongArtist] = useState('')
  const [songImage, setSongImage] = useState(
    'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
  )
  const [currentTime, setCurrentTime] = useState(0)
  const [duration, setDuration] = useState(300)
  const playerRef = useRef(null)
  const tokenRef = useRef(null)

  // on mount
  useEffect(() => {
    const urlParams = new URLSearchParams(window.location.search)
    const token = urlParams.get('token')
    const user_id = urlParams.get('user_id')
    localStorage.setItem('token', token)
    localStorage.setItem('user_id', user_id)
    setUserId(user_id)

    initPlayer(token).then((player) => {
      player.connect()
      player.addListener('ready', async ({ device_id }) => {
        localStorage.setItem('device_id', device_id)
        playerRef.current = player
        tokenRef.current = token
      })
    })

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
          window.addEventListener('beforeunload', function (event) {
            player.disconnect()
          })
          player.addListener(
            'player_state_changed',
            ({ position, duration, track_window: { current_track } }) => {
              setSongName(current_track['name'])
              setSongArtist(current_track['artists']['0']['name'])
              setSongImage(current_track['album']['images']['0']['url'])
              setCurrentTime(position)
              setDuration(duration)
            }
          )
          resolve(player)
        }
      })
    }
  }, [])

  useEffect(() => {
    let interval = null
    if (isPlaying) {
      interval = setInterval(() => {
        setCurrentTime((prevTime) => prevTime + 1000)
      }, 1000)
    } else if (!isPlaying && interval) {
      clearInterval(interval)
    }
    return () => {
      if (interval) {
        clearInterval(interval)
      }
    }
  }, [isPlaying])

  const handleSliderChange = (event) => {
    const newTime = Number(event.target.value)
    setCurrentTime(newTime)
    playerRef.current.seek(newTime)
  }

  // on playback state change
  useEffect(() => {
    console.log(`isPlayback: ${isPlayback}`)
    if (isPlayback) {
      setIsPlaying(true)
    } else {
      setSongName('')
      setSongArtist('')
      setSongImage(
        'data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7'
      )
      setIsPlaying(false)
    }
  }, [isPlayback])

  async function togglePlayerPlay() {
    if (isPlayback) {
      playerRef.current.togglePlay()
      setIsPlaying(!isPlaying)
    }
  }

  async function previous() {
    if (isPlayback) {
      playerRef.current.previousTrack()
      if (!isPlaying) {
        playerRef.current.togglePlay()
        setIsPlaying(true)
      }
    }
  }

  async function skip() {
    if (isPlayback) {
      playerRef.current.nextTrack()
      setIsPlaying(true)
    }
  }

  async function toggleShuffle() {
    const token = localStorage.getItem('token')
    const response = await fetch('http://127.0.0.1:5000/shuffle', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: token,
      }),
    })
    const data = await response.json()
    console.log(data)
    return data
  }

  return (
    <main>
      <div className="top-right">
        <h1>{userId}</h1>
      </div>
      <div className="top-left">
        <div className="song-info-container">
          <img src={songImage} className="song-image"></img>
          <div className="song-info">
            <h2>{songName}</h2>
            <h4>{songArtist}</h4>
          </div>
        </div>
        <div className="player-container">
          <button className="player-button" onClick={previous}>
            <img src="/prev.png" />
          </button>
          <button className="player-button" onClick={togglePlayerPlay}>
            <img src={isPlaying ? '/pause.png' : '/play.png'} />
          </button>
          <button className="player-button" onClick={skip}>
            <img src="/skip.png" />
          </button>
          <input
            type="range"
            min="0"
            max={duration}
            value={currentTime}
            onChange={handleSliderChange}
            className="playback-slider"
          />
        </div>
      </div>
    </main>
  )
}
