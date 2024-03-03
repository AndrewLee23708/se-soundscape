export class Pin {
    public name: string
    public lat: number
    public lng: number
    public playlist!: string
    public radius: number

    constructor(name: string, lat: number, lng: number) {
        this.name = name
        this.lat = lat
        this.lng = lng
        this.playlist = 'https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=7ad18edcdf164baa'
        this.radius = 1
      }
}