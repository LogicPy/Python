// frontend/src/App.js

import React, { useState, useEffect } from 'react';
import io from 'socket.io-client';
import GameRoom from './components/GameRoom';
import './App.css';

const socket = io('http://localhost:4000'); // Update with your backend URL

function App() {
  const [gameId, setGameId] = useState('');
  const [username, setUsername] = useState('');
  const [joined, setJoined] = useState(false);
  const [theme, setTheme] = useState('light'); // Theme state

  // Load theme from localStorage on initial render
  useEffect(() => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
      setTheme(savedTheme);
      document.documentElement.classList.toggle('dark-theme', savedTheme === 'dark');
    }
  }, []);

  // Update theme in DOM and localStorage when theme state changes
  useEffect(() => {
    if (theme === 'dark') {
      document.documentElement.classList.add('dark-theme');
    } else {
      document.documentElement.classList.remove('dark-theme');
    }
    localStorage.setItem('theme', theme);
  }, [theme]);

const joinGame = () => {
  if (gameId && username) {
    socket.emit('joinGame', { gameId, username }); // Ensure both are included
    setJoined(true);
  }
};

  const toggleTheme = () => {
    setTheme((prevTheme) => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Wordle Multiplayer</h1>
        <div className="toggle-switch">
          <input
            type="checkbox"
            id="theme-toggle-checkbox"
            onChange={toggleTheme}
            checked={theme === 'dark'}
          />
          <label htmlFor="theme-toggle-checkbox" className="toggle-label">
            <span className="toggle-inner"></span>
            <span className="toggle-switch"></span>
          </label>
        </div>
      </header>
      {!joined ? (
        <div className="join-game">
          <h2>Join a Wordle Game</h2>
          <input
            type="text"
            placeholder="Game ID"
            value={gameId}
            onChange={(e) => setGameId(e.target.value.toUpperCase())}
          />
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <button onClick={joinGame}>Join Game</button>
        </div>
      ) : (
        <GameRoom socket={socket} gameId={gameId} username={username} />
      )}
    </div>
  );
}

export default App;
