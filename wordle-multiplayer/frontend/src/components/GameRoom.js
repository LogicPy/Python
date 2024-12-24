import React, { useEffect, useState } from 'react';
import PlayerList from './PlayerList';
import GuessInput from './GuessInput';
import './GameRoom.css';

function GameRoom({ socket, gameId, username }) {
  const [players, setPlayers] = useState([]);
  const [guesses, setGuesses] = useState([]);
  const [feedbackList, setFeedbackList] = useState([]);
  const [gameOver, setGameOver] = useState(false);
  const [winner, setWinner] = useState('');
  const [aiGenerated, setAiGenerated] = useState(false); // AI word status

  useEffect(() => {
    socket.on('updatePlayers', (players) => {
      setPlayers(players);
    });

    socket.on('guessFeedback', (feedback) => {
      console.log('Received Feedback:', feedback);
      setFeedbackList((prevFeedbackList) => [...prevFeedbackList, feedback]);
    });

    socket.on('gameOver', ({ winner }) => {
      setGameOver(true);
      setWinner(winner);
    });

    socket.on('gameStart', ({ aiGenerated }) => {
      setAiGenerated(aiGenerated);
      resetGameState(); // Reset the local state when a new game starts
    });

    return () => {
      socket.off('updatePlayers');
      socket.off('guessFeedback');
      socket.off('gameOver');
      socket.off('gameStart');
    };
  }, [socket]);

  const resetGameState = () => {
    setGuesses([]);
    setFeedbackList([]);
    setGameOver(false);
    setWinner('');
  };

  const handleReset = () => {
    socket.emit('resetGame', { gameId }); // Emit reset event to the backend
  };

  const handleGuess = (guess) => {
    socket.emit('makeGuess', { gameId, guess });
    setGuesses([...guesses, guess.toUpperCase()]);
  };

  return (
    <div className="game-room">
      <h2>Game ID: {gameId}</h2>
      <PlayerList players={players} />
      <GuessInput onGuess={handleGuess} disabled={gameOver} />

      {aiGenerated && (
        <div className="ai-info">
          <p>The word was cleverly chosen by an AI opponent. Good luck!</p>
        </div>
      )}

      <div className="guesses">
        {guesses.map((guess, index) => (
          <div key={index} className="guess-row">
            {feedbackList[index] ? (
              feedbackList[index].map((f, i) => (
                <span
                  key={i}
                  className={`letter ${f.status}`}
                >
                  {f.letter}
                </span>
              ))
            ) : (
              guess.split('').map((letter, i) => (
                <span key={i} className="letter pending">
                  {letter}
                </span>
              ))
            )}
          </div>
        ))}
      </div>

      {gameOver && (
        <div className="game-over">
          <h2>Game Over!</h2>
          <p>{winner === socket.id ? 'You won!' : `${winner} won!`}</p>
        </div>
      )}

      <button className="reset-button" onClick={handleReset}>
        Reset Game
      </button>
    </div>
  );
}

export default GameRoom;
