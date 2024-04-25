'use client'
import React, { useState, useEffect } from 'react'
import { Loader } from '@googlemaps/js-api-loader'
const haversine = require('haversine')

const center = { lat: 40.72960320747002, lng: -73.99647715395606 }
const zoom = 15
let markerToggle = true

export default function Map() {
  useEffect(() => {
    async function init() {
      const apiKey = await fetchApiKey()
      const google = await loadGoogle(apiKey)
      const map = initMap(google, 'map')
      setGeolocation(google, map)
      setOnMapClick(google, map)
      debug()
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
      data.items.forEach((playlist) => {
        console.log(`name: ${playlist.name}, uri: ${playlist.uri}`)
      })
    }

    init()
    getPlaylists()
  }, [])

  return (
    <div>
      <div id="map"></div>
      <button id="marker">Marker</button>
      <button id="location">Location</button>
    </div>
  )
}

/**
 * @description Fetches client application Google Maps API key from backend endpoint
 * @returns {Promise<string>} Promise containing client application Google Maps API key
 */
async function fetchApiKey(): Promise<string> {
  const response = await fetch('http://127.0.0.1:5000/googlekey')
  const data = await response.json()
  return data.google_api_key
}

/**
 * @description Loads Google Maps API script into client application
 * @param {string} apiKey - Client application Google Maps API key
 * @returns {google} Returns reference to Google Maps API script
 */
async function loadGoogle(apiKey: string) {
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
  const map = new google.maps.Map(
    document.getElementById(mapElementId) as HTMLElement,
    {
      center: center,
      zoom: zoom,
      mapId: 'map',
    }
  )
  return map
}

/**
 * @description Initializes Google Maps Geolocation functions
 * @param {google} google - Reference to Google Maps API script
 * @param {map} map - Reference to Google Map
 * @description This function first sets map center to client current location. It then uses the watch position event to call the playbackCheck function whenever the client location changes.
 * @returns {void} Return nothing
 */
async function setGeolocation(google: any, map: any) {
  const marker = new google.maps.Marker({
    map: map,
    position: center,
  })
  if (navigator.geolocation) {
    navigator.geolocation.getCurrentPosition(
      (position: GeolocationPosition) => {
        const pos = {
          lat: position.coords.latitude,
          lng: position.coords.longitude,
        }
        map.setCenter(pos)
      }
    )
    navigator.geolocation.watchPosition((position: GeolocationPosition) => {
      const pos = {
        lat: position.coords.latitude,
        lng: position.coords.longitude,
      }
      const newPos = new google.maps.LatLng(pos)
      marker.setPosition(newPos)
      //playbackCheck(newPos)
    })
  }
}

/**
 * @description Sets on click events for Google Map
 * @param {google} google - Reference to Google Maps API script
 * @param {map} map - Reference to Google Map
 * @description On map click, the click coordinates will be determined, a pin object will be created with click position coordinates and stored in the backend, a marker object is created and centered on the click position, on click event functions are set for the marker, and a Google Maps circle is created centered at click position with radius of the pin object.
 * @returns {void} Return nothing
 */
async function setOnMapClick(google: any, map: any) {
  map.addListener('click', async (mapsMouseEvent: { latLng: any }) => {
    const position = mapsMouseEvent.latLng
    if (markerToggle) {
      // create pin in backend
      const pin = {
        name: 'Pin',
        position: position,
        radius: 1000,
        uri: 'spotify:album:5ht7ItJgpBH7W6vJ5BqpPr',
      }
      const pinString = JSON.stringify(pin)
      const id = generatePinId()
      localStorage.setItem(id, pinString) // store via endpoint instead

      // create marker in google map
      const marker = new google.maps.Marker({
        map: map,
        position: position,
        title: pin.name,
      })
      marker.id = id

      // create radius indicator in google map
      const circle = new google.maps.Circle({
        map: map,
        radius: pin.radius,
        fillColor: '#21D060',
        fillOpacity: 0.5,
        strokeColor: '#21D060',
        strokeOpacity: 0.5,
        strokeWeight: 2,
        center: position,
        clickable: false,
      })

      // set marker on click event
      setOnMarkerClick(google, map, pin, marker, circle)
    } else {
      playbackCheck(position)
    }
  })
}

/**
 * @description Checks what the state of playback needs to be at position
 * @param {google.maps.LatLng} position - Google Maps position object
 * @description This function checks if the position is within radius of any pins. If it is, it will begin playback of the returned pin. If not, then playback will stop.
 * @returns {void} Return nothing
 */
function playbackCheck(position) {
  const pin = radiusCheck(position)
  if (pin != -1) {
    playPin(pin)
  } else {
    stopPlayback()
  }
}

/**
 * @description Returns first pin position is within radius of
 * @param {google.maps.LatLng} position - Google Maps position object
 * @description This function fetches all pins currently stored for the client. It then checks the haversine distance from the given position to all of the client's pins. It returns the first pin that is within range, or -1 if no pins are within range.
 * @returns {pin} Return pin object
 */
function radiusCheck(position: any) {
  console.log(`radius checking at (${position.lat()}, ${position.lng()})`)
  const pins = fetchPins()
  for (let i = 0; i < pins.length; i++) {
    const pin = pins[i]
    const distance = haversine(
      {
        latitude: position.lat(),
        longitude: position.lng(),
      },
      {
        latitude: pin.position.lat,
        longitude: pin.position.lng,
      },
      { unit: 'meter' }
    )

    if (distance <= pin.radius) {
      return pin
    }
  }

  return -1
}

// call fetchpin endpoint instead                                               
/**
 * @description Fetches all pin objects from storage
 * @returns {pin[]} Returns array of pin objects
 */
function fetchPins() {
  const urlParams = new URLSearchParams(window.location.search);
  const userId = urlParams.get('user_id');

  return fetch(`http://localhost:5000/user/${userId}/pins`, {  // Correctly using userId in the endpoint
    method: 'GET',
    headers: {
      'Content-Type': 'application/json'
    }
  })
  .then(response => response.json())
  .then(data => {
    console.log('Pins:', data);
    return data;
  })
  .catch(error => {
    console.error('Error fetching pins:', error);
  });
}



//   let pins = []
//   for (let i = 0; i < localStorage.length; i++) {
//     const key = localStorage.key(i)
//     if (key.startsWith('pin_')) {
//       const pinData = localStorage.getItem(key)
//       if (pinData) {
//         pins.push(JSON.parse(pinData))
//       }
//     }
//   }
//   return pins
// }




// template POST request
/**
 * @description Starts playback context corresponding to given pin
 * @param {pin} pin - Pin object
 * @description Calls backend function to begin playback given the pin's playlist uri
 * @returns {void} Returns nothing
 */
async function playPin(pin: any) {
  const token = localStorage.getItem('token')
  const device_id = localStorage.getItem('device_id')
  const response = await fetch('http://127.0.0.1:5000/play', {
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
  const data = await response.json()
  console.log(data.message)
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
  console.log(data.message)
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
function setOnMarkerClick(google: any, map: any, pin: any, marker: any, circle: any) {
  marker.addListener('click', () => {
    const infoWindow = new google.maps.InfoWindow({
      content: createInfoWindowContent(pin, marker, circle),
    })
    infoWindow.open(map, marker)
  })
}

// use modify pin endpoint instead
/**
 * @description Returns info window for Google Map markers
 * @param {pin} pin - Pin object
 * @param {marker} marker - Reference to Google Maps API marker
 * @param {circle} circle - Google Maps circle object
 * @description Creates a custom HTML edit pop up window for markers. Upon clicking save button, pin in storage will be updated to reflect the changes.
 * @returns {div} Returns HTML div element
 */
function createInfoWindowContent(pin, marker, circle) {
  const div = document.createElement('div')
  div.innerHTML = `
      <label>Name:</label>
      <input id="name" type="text" value="${pin.name}" /><br>
      <label>URI:</label>
      <input id="uri" type="text" value="${pin.uri}" /><br>
      <label>Radius:</label>
      <input id="radius" type="text" value="${pin.radius}" /><br>
      <button id="save">Save</button>
    `
  const button = div.querySelector('#save')
  button.addEventListener('click', function () {
    const newName = div.querySelector('#name').value
    pin.name = newName
    const newUri = div.querySelector('#uri').value
    pin.uri = newUri
    const newRadius = parseFloat(div.querySelector('#radius').value);
    pin.radius = newRadius
    circle.setRadius(newRadius)
    const pinString = JSON.stringify(pin)

    // modify to use modify pin endpoint
    localStorage.setItem(marker.id, pinString)
  })
  return div
}

/**
 * @description Returns random Pin ID for keeping track of pins
 * @param {int} length - Length of random string
 * @returns {string} Returns pin ID
 */
function generatePinId(length = 8) {
  let result = 'pin_'
  const characters =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length))
  }
  return result
}

/**
 * @description Enables debugging tools like editing current location
 * @param {int} length - Length of random string
 * @returns {void} Returns nothing
 */
function debug() {
  document.getElementById('marker').onclick = function () {
    markerToggle = true
  }
  document.getElementById('location').onclick = function () {
    markerToggle = false
  }
}
