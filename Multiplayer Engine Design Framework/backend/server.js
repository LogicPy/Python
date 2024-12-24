const express = require("express");
const http = require("http");
const socketIo = require("socket.io");

const app = express();
const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: "*",
    methods: ["GET", "POST"],
  },
});

const PORT = 4005;

const lobbies = {}; // Store lobbies and their messages

io.on("connection", (socket) => {
  console.log(`New client connected: ${socket.id}`);

socket.on("joinLobby", ({ username, lobbyName }) => {
  socket.join(lobbyName);

  // Prevent broadcasting "joined lobby" repeatedly
  if (!lobbies[lobbyName]) {
    lobbies[lobbyName] = []; // Initialize the lobby
  }

  // Notify once when a user joins
  if (!lobbies[lobbyName].includes(username)) {
    lobbies[lobbyName].push(username);
    io.to(lobbyName).emit("receiveMessage", {
      username: "System",
      message: `${username} has joined the lobby.`,
    });
  }

  console.log(`${username} joined lobby: ${lobbyName}`);
});


  socket.on("sendMessage", ({ lobbyName, username, message }) => {
    const data = { username, message };
    lobbies[lobbyName].push(data); // Store the message in the lobby
    io.to(lobbyName).emit("receiveMessage", data); // Broadcast to everyone in the lobby
  });

  socket.on("disconnect", () => {
    console.log(`Client disconnected: ${socket.id}`);
  });
});

server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
