'use client'

import type { NextPage } from 'next'
import Button from "./CreateButton"
import express from "express";
import querystring from 'querystring';

var client_id = '4e06e42c224a4a72bc9841288c926121';
var redirect_uri = 'http://localhost:3000/';

var app = express();

app.get('/login', function(req, res) {

  var state = generateRandomString(16);
  var scope = 'user-read-private user-read-email';

  res.redirect('https://accounts.spotify.com/authorize?' +
    querystring.stringify({
      response_type: 'code',
      client_id: client_id,
      scope: scope,
      redirect_uri: redirect_uri,
      state: state
    }));
});


const Home: NextPage = () => {
  return (
    <main>
      <div>
        <h1>Soundscapes</h1>
        <button onClick={() => login()}>Log in with Spotify</button>
      </div>
    </main>
  )
}

const login = async () => {
  window.location.href = 'http://localhost:3000/map'
}

export default Home

function generateRandomString(length: number): string {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
}