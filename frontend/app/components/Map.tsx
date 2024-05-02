'use client'
import React, { useState, useEffect, useRef } from 'react'
import ReactDOM from 'react-dom'
import { Loader } from '@googlemaps/js-api-loader'
import Player from '../components/Player'
const haversine = require('haversine')

const center = { lat: -77.27235939142727, lng: 94.45058478512921 }
let markerToggle = true

export default function Map() {
  const [isPlayback, setIsPlayback] = useState(false)
  const [isMarker, setIsMarker] = useState(false)
  const googleRef = useRef(null)
  const mapRef = useRef(null)
  const currentLocationMarkerRef = useRef(null)

  const [currentPosition, setCurrentPosition] = useState({
    lat: 1000000,
    lng: 1000000,
  })

  useEffect(() => {
    async function init() {
      const apiKey = await fetchGoogleApiKey()
      const google = await loadGoogleApi(apiKey)
      googleRef.current = google
      const map = initMap(google, 'map')
      mapRef.current = map
      setGeolocation(google, map)
      const pins = await fetchPins()
      await initPins(map, pins)
      setIsMarker(true)
      //await getPlaylists()
    }

    init()
  }, [])

  useEffect(() => {
    console.log(
      `currentPosition: (${currentPosition.lat}, ${currentPosition.lng})`
    )
    if (mapRef.current) {
      const newPos = new google.maps.LatLng(currentPosition)
      currentLocationMarkerRef.current.setPosition(newPos)
    }
    playbackCheck(currentPosition)

    async function playbackCheck(position) {
      const pin = await radiusCheck(position)
      if (pin != -1 && pin.uri != 'empty') {
        if (isPlayback) {
          return
        }
        await playPin(pin)
      } else {
        await stopPlayback()
      }
    }
  }, [currentPosition, isPlayback])

  useEffect(() => {
    console.log(`setting map marker event to ${isMarker}`)

    if (!mapRef.current) {
      return
    }

    const map = mapRef.current
    const google = googleRef.current

    const listener = map.addListener('click', async (mapsMouseEvent) => {
      const position = mapsMouseEvent.latLng
      if (isMarker) {
        // create pin in backend
        const pin = {
          name: 'Pin',
          lat: position.lat(),
          lng: position.lng(),
          radius: 1000,
          uri: 'empty',
          id: -1,
        }
        const id = await createPin(pin)
        pin.id = id
        createMapElements(map, pin)
      } else {
        setCurrentPosition({ lat: position.lat(), lng: position.lng() })
      }
    })
    return () => {
      google.maps.event.removeListener(listener)
    }
  }, [isMarker])

  // ==================================================
  // ================  INITIALIZATION  ================
  // ==================================================

  /**
   * @description Fetches client application Google Maps API key from backend endpoint
   * @returns {Promise<string>} Promise containing client application Google Maps API key
   */
  async function fetchGoogleApiKey(): Promise<string> {
    const response = await fetch('http://127.0.0.1:5000/googlekey')
    const data = await response.json()
    return data.google_api_key
  }

  /**
   * @description Loads Google Maps API script into client application
   * @param {string} apiKey - Client application Google Maps API key
   * @returns {google} Returns reference to Google Maps API script
   */
  async function loadGoogleApi(apiKey: string) {
    const loader = new Loader({
      apiKey: apiKey,
      version: 'weekly',
    })

    await loader.load()
    return google
  }

  /**
   * @description Initializes Google Map at document map div
   * @param {google} google - Reference to Google Maps API script
   * @param {string} mapElementId - ID of document element Google Map will be instantiated in
   * @returns {map} Returns reference to the newly instantiated Google Map object
   */
  function initMap(google: any, mapElementId: string) {
    const allowedBounds = new google.maps.LatLngBounds(
      new google.maps.LatLng(-85.04, -179.782),
      new google.maps.LatLng(85.229, 179.753)
    )

    const map = new google.maps.Map(
      document.getElementById(mapElementId) as HTMLElement,
      {
        center: center,
        zoom: 15,
        mapId: '35263e0e6da7fc09',
        streetViewControl: false,
        mapTypeControl: false,
        zoomControl: false,
        rotateControl: false,
        fullscreenControl: false,
        restriction: {
          latLngBounds: allowedBounds,
          strictBounds: true, // Optional: set to `true` to strictly enforce the bounds
        },
      }
    )
    return map
  }

  async function initPins(map: any, pins: any) {
    for (const pin of pins) {
      await createMapElements(map, pin)
    }
  }

  /**
   * @description Initializes Google Maps Geolocation functions
   * @param {google} google - Reference to Google Maps API script
   * @param {map} map - Reference to Google Map
   * @description This function first sets map center to client current location. It then uses the watch position event to call the playbackCheck function whenever the client location changes.
   * @returns {void} Return nothing
   */
  async function setGeolocation(google: any, map: any) {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position: GeolocationPosition) => {
          const pos = {
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          }
          const currentLocationImg = document.createElement('img')
          currentLocationImg.src = '/location.png'
          const marker = new google.maps.Marker({
            map: mapRef.current,
            position: center,
            content: currentLocationImg,
          })
          currentLocationMarkerRef.current = marker
          map.setCenter(pos)
          setCurrentPosition(pos)
        }
      )
      navigator.geolocation.watchPosition((position: GeolocationPosition) => {
        const pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        }
        //setCurrentPosition(pos)
      })
    }
  }

  // ==================================================
  // ================  BACKEND INTERFACE ==============
  // ==================================================

  /**
   * @description Fetches all pin objects from database
   * @returns {pin[]} Returns array of pin objects
   */
  async function fetchPins() {
    const user_id = localStorage.getItem('user_id')
    const response = await fetch('http://127.0.0.1:5000/fetchpins', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: user_id,
      }),
    })
    const data = await response.json()
    const raw_pins = data.pins

    const pins = []
    for (const raw_pin of raw_pins) {
      const pin = {
        name: raw_pin['Name'],
        lat: raw_pin['Latitude'],
        lng: raw_pin['Longitude'],
        radius: raw_pin['Radius'],
        uri: raw_pin['URI'],
        id: raw_pin['Pin_ID'],
      }
      pins.push(pin)
    }
    return pins
  }

  async function createPin(pin: any) {
    const user_id = localStorage.getItem('user_id')
    const response = await fetch('http://127.0.0.1:5000/createpin', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: user_id,
        pin: pin,
      }),
    })
    const data = await response.json()
    const id = data.pin_id
    console.log(data)
    return id
  }

  async function editPin(pin_id: any, pin: any) {
    console.log('editing pin')
    console.log(pin_id)
    console.log(pin)
    const user_id = localStorage.getItem('user_id')
    const response = await fetch('http://127.0.0.1:5000/editpin', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: user_id,
        pin_id: pin_id,
        pin: pin,
      }),
    })
    const data = response.json()
    console.log(data)
    return
  }

  async function deletePin(pin_id: any) {
    const user_id = localStorage.getItem('user_id')
    const response = await fetch('http://127.0.0.1:5000/deletepin', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        user_id: user_id,
        pin_id: pin_id,
      }),
    })
  }

  // ==================================================
  // ================  UI FUNCTIONS    ================
  // ==================================================

  async function createMapElements(map: any, pin: any) {
    const position = new google.maps.LatLng(pin.lat, pin.lng)

    // create marker in google map
    const marker = new google.maps.Marker({
      map: map,
      position: position,
      title: pin.name,
    })
    marker.playlistName = await getPlaylistName(pin.uri)

    // create radius indicator in google map
    const circle = new google.maps.Circle({
      map: map,
      radius: pin.radius,
      fillColor: '#007bff',
      fillOpacity: 0.5,
      strokeColor: '#007bff',
      strokeOpacity: 0.5,
      strokeWeight: 2,
      center: position,
      clickable: false,
    })

    // set marker on click event
    await setOnMarkerClick(google, map, pin, marker, circle)
  }

  /**
   * @description Starts playback context corresponding to given pin
   * @param {google} google - Reference to Google Maps API script
   * @param {map} map - Reference to Google Map
   * @param {pin} pin - Pin object
   * @param {marker} marker - Reference to Google Maps API marker
   * @param {circle} circle - Google Maps circle object
   * @description This function sets the marker to have a pop up window which pops up when clicked
   * @returns {void} Returns nothing
   */
  async function setOnMarkerClick(
    google: any,
    map: any,
    pin: any,
    marker: any,
    circle: any
  ) {
    marker.addListener('click', async () => {
      const infoWindow = new google.maps.InfoWindow({
        content: await createInfoWindow(pin, marker, circle),
      })
      infoWindow.open(map, marker)
      infoWindow.addListener('closeclick', function () {
        circle.setRadius(pin.radius)
      })
    })
  }

  /**
   * @description Returns info window for Google Map markers
   * @param {pin} pin - Pin object
   * @param {marker} marker - Reference to Google Maps API marker
   * @param {circle} circle - Google Maps circle object
   * @description Creates a custom HTML edit pop up window for markers. Upon clicking save button, pin in storage will be updated to reflect the changes.
   * @returns {div} Returns HTML div element
   */
  async function createInfoWindow(pin, marker, circle) {
    const div = document.createElement('div')
    div.innerHTML = `
    <label>Name:  </label>
      <input id="name" type="text" value="${pin.name}" /><br>
      <label>Playlist:</label>
      <input id="uri" type="text" value="${marker.playlistName}" /><br>
      <label>Radius:</label>
      <input id="radius" type="range" min="100" max="10000" value="${pin.radius}" step="100" /><br>
      <span id="radius-value">${pin.radius} Meters</span><br><br>
      <button id="save">Save</button>
      <button id="delete">Delete</button>
    `

    const radiusInput = div.querySelector('#radius')
    const radiusValueSpan = div.querySelector('#radius-value')

    radiusInput.addEventListener('input', function () {
      const newRadius = parseFloat(radiusInput.value)
      radiusValueSpan.textContent = `${newRadius} Meters`
      circle.setRadius(newRadius)
    })

    const saveBtn = div.querySelector('#save')
    saveBtn.addEventListener('click', async function () {
      const newName = div.querySelector('#name').value
      pin.name = newName

      // find playlist uri from playlist name and set new uri
      const newPlaylistName = div.querySelector('#uri').value
      const newUri = await getPlaylistUri(newPlaylistName)
      
      console.log(`new playlist name ${newPlaylistName}`)
      console.log(`new playlist uri ${newUri}`)
      marker.playlistName = newPlaylistName
      pin.uri = newUri

      const newRadius = parseFloat(radiusInput.value)
      pin.radius = newRadius
      await editPin(pin.id, pin) // Save the updated pin information
    })

    const delBtn = div.querySelector('#delete')
    delBtn.addEventListener('click', async function () {
      await deletePin(pin.id)
      deleteMapElements(marker, circle) // Remove the marker and circle from the map
    })

    return div
  }

  async function deleteMapElements(marker: any, circle: any) {
    if (marker.infoWindow) {
      marker.infoWindow.close()
    }
    marker.setMap(null)
    circle.setMap(null)
  }

  // ==================================================
  // ================  PLAYBACK FUNCTIONS  ============
  // ==================================================

  async function radiusCheck(position: any) {
    const pins = await fetchPins()
    for (const pin of pins) {
      const distance = haversine(
        {
          latitude: position.lat,
          longitude: position.lng,
        },
        {
          latitude: pin.lat,
          longitude: pin.lng,
        },
        { unit: 'meter' }
      )
      if (distance <= pin.radius) {
        return pin
      }
    }
    return -1
  }

  /*
   * @description Starts playback context corresponding to given pin
   * @param {pin} pin - Pin object
   * @description Calls backend function to begin playback given the pin's playlist uri
   * @returns {void} Returns nothing
   */
  async function playPin(pin: any) {
    const token = localStorage.getItem('token')
    const device_id = localStorage.getItem('device_id')
    let response = await fetch('http://127.0.0.1:5000/play', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: token,
        device_id: device_id,
        uri: pin.uri,
      }),
    })
    let data = await response.json()
    console.log(data.message)
    setIsPlayback(true)
  }

  /**
   * @description Starts playback context corresponding to given pin
   * @description Calls backend function to stop all playback
   * @returns {void} Returns nothing
   */
  async function stopPlayback() {
    const token = localStorage.getItem('token')
    const device_id = localStorage.getItem('device_id')
    const response = await fetch('http://127.0.0.1:5000/pause', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: token,
        device_id: device_id,
      }),
    })
    const data = await response.json()
    setIsPlayback(false)
  }

  // ==================================================
  // ================  DEBUG FUNCTIONS  ===============
  // ==================================================

  async function getPlaylistUri(playlistName: any) {
    const playlists = await getPlaylists()
    for (const playlist of playlists) {
      if (playlist.name == playlistName) {
        console.log(playlist.name)
        return playlist.uri
      }
    }
    return ''
  }

  async function getPlaylistName(playlistUri: any) {
    const playlists = await getPlaylists()
    for (const playlist of playlists) {
      if (playlist.uri == playlistUri) {
        console.log(playlist.uri)
        return playlist.name
      }
    }
    return ''
  }

  async function getPlaylists() {
    const token = localStorage.getItem('token')
    const response = await fetch('http://127.0.0.1:5000/playlists', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        token: token,
      }),
    })
    const data = await response.json()
    return data.items
  }

  return (
    <div>
      <div id="map"></div>
      <Player isPlayback={isPlayback} />
      <div className="bottom-right debug-button-container">
        <button
          id="marker"
          className={isMarker ? 'btn btn-primary' : 'btn btn-outline-primary'}
          onClick={() => {
            setIsMarker(true)
          }}
        >
          Marker
        </button>
        <button
          id="location"
          className={!isMarker ? 'btn btn-primary' : 'btn btn-outline-primary'}
          onClick={() => {
            setIsMarker(false)
          }}
        >
          Location
        </button>
      </div>
    </div>
  )
}
