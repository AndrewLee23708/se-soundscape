"use client"

export default function CreateButton() {
  return (<button className="btn btn-lg btn-primary" onClick={() => login()}>Listen to your surroundings...</button>)
}

const login = async () => {
  try {
    let response = await fetch('https://accounts.spotify.com/authorize?' + querystring.stringify({
      client_id: '4e06e42c224a4a72bc9841288c926121',
      response_type: 'code',
      redirect_uri: 'http://localhost:3000/',
      scope: 'user-read-private user-read-email'
    }));
    let url = await response.text();
    window.location.href = url;
  } catch (error) {
    console.log(`ERROR ${error}`);
  }
}
