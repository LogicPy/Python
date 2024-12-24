const axios = require('axios'); // For making API requests
const express = require('express');
const http = require('http');
const socketIo = require('socket.io');
const cors = require('cors');

const app = express();
app.use(cors());

const server = http.createServer(app);
const io = socketIo(server, {
  cors: {
    origin: '*', // Update with your frontend URL in production
    methods: ['GET', 'POST']
  }
});

const PORT = process.env.PORT || 4000; // Declare PORT with a default value
const WORD_LIST = ['XENON', 'APPLE', 'BANJO', 'CRANE', 'DOUBT', 'EAGLE']; // Sample fallback word list
const games = {}; // Global object to store game data

// Fetch a word using AI or fall back to the predefined list
async function getAIWord() {
  try {
    const response = await axios.post('http://localhost:5000/groq', {
      content: "Think of a five-letter word for Wordle.",
    });
    return response.data.word.toUpperCase(); // Ensure the word is uppercase
  } catch (error) {
    console.error("Error fetching AI word:", error);
    return WORD_LIST[Math.floor(Math.random() * WORD_LIST.length)]; // Fallback
  }
}

// WebSocket connection handler
io.on('connection', (socket) => {
  console.log(`New client connected: ${socket.id}`);

  // Handle the 'joinGame' event
  socket.on('joinGame', async ({ gameId, username }) => {
    if (!gameId || !username) {
      console.error('Game ID or username is missing in joinGame payload');
      return;
    }

    if (!games[gameId]) {
      const aiWord = await getAIWord(); // Fetch AI-generated word
      games[gameId] = {
        players: [],
        targetWord: aiWord,
        guesses: {}
      };
    }

    const game = games[gameId];
    game.players.push({ id: socket.id, username });
    game.guesses[socket.id] = [];

    socket.join(gameId);
    io.to(gameId).emit('updatePlayers', game.players.map(p => p.username));

    // Notify the players that the word was AI-generated
    io.to(gameId).emit('gameStart', { aiGenerated: true });

    console.log(`${username} joined game ${gameId}`);
    console.log(`Game ID: ${gameId}, Target Word: ${game.targetWord}`);
  });

  // Handle the 'makeGuess' event
  socket.on('makeGuess', ({ gameId, guess }) => {
    const game = games[gameId];
    if (!game) return;

    game.guesses[socket.id].push(guess);

    const feedback = evaluateGuess(guess, game.targetWord);

    io.to(socket.id).emit('guessFeedback', feedback);

    if (guess.toUpperCase() === game.targetWord) {
      io.to(gameId).emit('gameOver', { winner: socket.id });
    }
  });

  // Handle client disconnection
  socket.on('disconnect', () => {
    console.log(`Client disconnected: ${socket.id}`);
    for (const gameId in games) {
      const game = games[gameId];
      game.players = game.players.filter(p => p.id !== socket.id);
      delete game.guesses[socket.id];
      io.to(gameId).emit('updatePlayers', game.players.map(p => p.username));
      if (game.players.length === 0) {
        delete games[gameId];
      }
    }
  });
});

socket.on('resetGame', async ({ gameId }) => {
  if (!games[gameId]) return;
  const newWord = await getAIWord();
  games[gameId].targetWord = newWord;
  games[gameId].guesses = {};
  io.to(gameId).emit('gameStart', { aiGenerated: true });
});


// Function to evaluate guesses
function evaluateGuess(guess, target) {
  guess = guess.toUpperCase();
  target = target.toUpperCase();
  const feedback = [];

  for (let i = 0; i < 5; i++) {
    if (guess[i] === target[i]) {
      feedback.push({ letter: guess[i], status: 'correct' });
    } else if (target.includes(guess[i])) {
      feedback.push({ letter: guess[i], status: 'present' });
    } else {
      feedback.push({ letter: guess[i], status: 'absent' });
    }
  }

  return feedback;
}

server.listen(PORT, () => console.log(`Server running on port ${PORT}`));
