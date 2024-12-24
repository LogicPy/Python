// frontend/src/components/PlayerList.js

import React from 'react';
import './PlayerList.css';

function PlayerList({ players }) {
  return (
    <div className="player-list">
      <h3>Players:</h3>
      <ul>
        {players.map((player, index) => (
          <li key={index}>{player}</li>
        ))}
      </ul>
    </div>
  );
}

export default PlayerList;
