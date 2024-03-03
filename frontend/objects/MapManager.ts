import { Loader } from '@googlemaps/js-api-loader'
import { Pin } from './Pin'

export class MapManager {
  private user: string
  private profile: string
  private map!: google.maps.Map
  private markerMap: Map<any, Pin> = new Map()
  private pinCount: number = 0

  constructor(user: string, profile: string) {
    this.user = user
    this.profile = profile
  }

  public initMap(): void {
    // import google maps api
    const loader = new Loader({
      apiKey: 'AIzaSyCZw0dvbASvPG8mfGuwgKwmjq6CBKAWPxw',
      version: 'weekly',
    })
    loader
      .load()
      .then(async () => {
        const { Map } = (await google.maps.importLibrary(
          'maps'
        )) as google.maps.MapsLibrary
        const { AdvancedMarkerElement } = (await google.maps.importLibrary(
          'marker'
        )) as google.maps.MarkerLibrary

        // initialize map element
        this.map = new Map(document.getElementById('map') as HTMLElement, {
          center: { lat: 40.72960320747002, lng: -73.99647715395606 },
          zoom: 15,
          mapId: `${this.user}_MAP`,
        })

        // on map clicked event function
        this.map.addListener('click', (mapsMouseEvent: { latLng: any }) => {
          const position = mapsMouseEvent.latLng // get position of mouse click

          // add advanced marker element to map element
          const marker = new AdvancedMarkerElement({
            map: this.map,
            position: position,
            title: 'Pin',
          })

          // map advanced marker element to a new pin object with the same position
          this.markerMap.set(
            marker,
            this.createPin(position.lat(), position.lng())
          )

          // on marker clicked event function
          marker.addListener('click', () => {
            const pin = this.markerMap.get(marker) // fetch pin instance from marker map
            if (!pin) return

            // create info window based on pin information
            const infoWindow = new google.maps.InfoWindow({
              content: `<h1>${pin.name}</h1>
              <p>(${pin.lat}, ${pin.lng})</p>
              <p>${pin.playlist}</p>
              <p>Radius: ${pin.radius}</p>
              <button>Edit Pin</button>`,
            })
            infoWindow.open(this.map, marker) // open info window on marker on the map
          })
        })
      })
      .catch((e) => {
        console.error('Error loading the Google Maps script', e)
      })
  }

  private createPin(lat: number, lng: number): Pin {
    this.pinCount = this.pinCount + 1
    return new Pin(`Pin ${this.pinCount}`, lat, lng)
  }
}
