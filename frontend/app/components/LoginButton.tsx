"use client"

export default function LoginButton() {
  return (<button type="button" className="btn btn-lg btn-success login-btn" onClick={() => login()}>Log In With Spotify</button>)
}

const login = async () => {
  try {
    window.location.href = 'http://127.0.0.1:5000/login'
  } catch (error) {
    console.log(`ERROR ${error}`)
  }
}