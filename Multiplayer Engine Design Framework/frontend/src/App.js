import React, { useState, useEffect } from "react";
import { io } from "socket.io-client";
import './App.css';

const socket = io('http://localhost:4005'); // Backend URL

function App() {
  const [lobbyName, setLobbyName] = useState('');
  const [username, setUsername] = useState('');
  const [messages, setMessages] = useState([]);
  const [messageInput, setMessageInput] = useState('');
  const [loggedIn, setLoggedIn] = useState(false);

  // Register socket event listeners
  useEffect(() => {
    socket.on('receiveMessage', (data) => {
      setMessages((prevMessages) => [...prevMessages, data]);
    });

    return () => {
      socket.off('receiveMessage'); // Clean up the listener when the component unmounts
    };
  }, []);

  const handleLogin = () => {
    if (username && lobbyName) {
      socket.emit('joinLobby', { username, lobbyName });
      setLoggedIn(true);
    } else {
      alert("Please enter both a username and lobby name.");
    }
  };

  const sendMessage = () => {
    if (messageInput) {
      socket.emit('sendMessage', { lobbyName, username, message: messageInput });
      setMessageInput('');
    }
  };

  return (
    <div>
      {!loggedIn ? (
        <div>
          <h1>Welcome to the Multiplayer Game Engine</h1>
          <input
            type="text"
            placeholder="Enter your username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            type="text"
            placeholder="Enter a lobby name"
            value={lobbyName}
            onChange={(e) => setLobbyName(e.target.value)}
          />
          <button onClick={handleLogin}>Join Lobby</button>
        </div>
      ) : (
        <div>
          <h1>Lobby: {lobbyName}</h1>
          <div className="chat-box">
            {messages.map((msg, index) => (
              <p key={index}>
                <strong>{msg.username}</strong>: {msg.message}
              </p>
            ))}
          </div>
          <input
            type="text"
            placeholder="Type a message..."
            value={messageInput}
            onChange={(e) => setMessageInput(e.target.value)}
          />
          <button onClick={sendMessage}>Send</button>
        </div>
      )}
    </div>
  );
}

export default App;
