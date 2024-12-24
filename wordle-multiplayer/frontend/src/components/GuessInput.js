// frontend/src/components/GuessInput.js

import React, { useState } from 'react';
import './GuessInput.css';

function GuessInput({ onGuess, disabled }) {
  const [guess, setGuess] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (guess.length === 5) {
      onGuess(guess);
      setGuess('');
    } else {
      alert('Please enter a 5-letter word.');
    }
  };

  return (
    <form className="guess-input" onSubmit={handleSubmit}>
      <input
        type="text"
        maxLength="5"
        value={guess}
        onChange={(e) => setGuess(e.target.value.toUpperCase())}
        placeholder="Enter your guess"
        disabled={disabled}
      />
      <button type="submit" disabled={disabled}>
        Guess
      </button>
    </form>
  );
}

export default GuessInput;

