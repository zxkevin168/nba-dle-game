import React, { useState, useEffect } from 'react';

// The main application component for the NBA-dle game.
const App = () => {
    // State variables to manage the game's data and UI.
    const [clues, setClues] = useState({});
    const [guess, setGuess] = useState('');
    const [guesses, setGuesses] = useState([]);
    const [message, setMessage] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [isPlayerFound, setIsPlayerFound] = useState(false);
    const [allPlayers, setAllPlayers] = useState([]);
    const [filteredPlayers, setFilteredPlayers] = useState([]);
    const [guessCount, setGuessCount] = useState(0);

    // Base URL for the backend API.
    const API_BASE_URL = 'http://127.0.0.1:5000';

    // Fetches all active players from the backend for the autocomplete.
    const fetchAllPlayers = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/players`);
            if (!response.ok) {
                throw new Error('Failed to fetch players list');
            }
            const data = await response.json();
            setAllPlayers(data);
        } catch (error) {
            console.error("Error fetching all players:", error);
        }
    };

    // Fetches the daily player's clues from the backend API.
    const fetchDailyPlayerClues = async () => {
        try {
            const response = await fetch(`${API_BASE_URL}/api/daily-player`);
            if (!response.ok) {
                throw new Error('Failed to fetch daily player clues');
            }
            const data = await response.json();
            setClues(data);
        } catch (error) {
            console.error("Error fetching daily player clues:", error);
            setMessage("Failed to load clues. Please try again later.");
        }
    };

    // Handles the submission of a user's guess.
    const handleGuessSubmit = async (e) => {
        e.preventDefault();
        setIsLoading(true);
        setMessage('');

        // Find the full player name from the allPlayers list
        const guessedPlayer = allPlayers.find(p => p.full_name.toLowerCase() === guess.toLowerCase());
        if (!guessedPlayer) {
            setMessage('Please select a valid player from the dropdown.');
            setIsLoading(false);
            return;
        }

        try {
            const response = await fetch(`${API_BASE_URL}/api/check-guess`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ guess: guessedPlayer.full_name }),
            });

            if (!response.ok) {
                throw new Error('Failed to submit guess');
            }

            const data = await response.json();
            
            setGuessCount(prev => prev + 1);

            // Construct the new guess object.
            const newGuess = {
                guessName: data.feedback?.guessed_player_name || guess,
                feedback: data.feedback,
                correct: data.correct,
                message: data.message,
            };

            // If the guess is correct, manually fill in the feedback from the clues.
            if (newGuess.correct) {
                newGuess.feedback = {
                    guessed_player_name: newGuess.guessName,
                    guessed_team: clues.team_name,
                    guessed_position: clues.position,
                    guessed_jersey: clues.jersey,
                    team_match: true,
                    position_match: true,
                    jersey_match: true,
                    jersey_hint: null
                };
            }

            // Add the new guess to the list of guesses.
            setGuesses(prevGuesses => [
                ...prevGuesses,
                newGuess,
            ]);

            // Update the message and game state based on the response.
            setMessage(data.message);
            setIsPlayerFound(data.correct);
            setGuess(''); // Clear the input field.
            setFilteredPlayers([]); // Clear the dropdown.

        } catch (error) {
            console.error("Error submitting guess:", error);
            setMessage("An error occurred while checking your guess.");
        } finally {
            setIsLoading(false);
        }
    };

    // Handles changes to the input field for autocomplete.
    const handleInputChange = (e) => {
        const value = e.target.value;
        setGuess(value);

        if (value.length > 0) {
            const filtered = allPlayers.filter(player =>
                player.full_name.toLowerCase().startsWith(value.toLowerCase())
            );
            setFilteredPlayers(filtered.slice(0, 10)); // Show up to 10 results
        } else {
            setFilteredPlayers([]);
        }
    };

    // Handles selection from the autocomplete dropdown.
    const handlePlayerSelect = (playerName) => {
        setGuess(playerName);
        setFilteredPlayers([]); // Hide the dropdown
    };

    // Fetches the initial clues and player list when the component mounts.
    useEffect(() => {
        fetchAllPlayers();
        fetchDailyPlayerClues();
    }, []);

    // Renders a single guess with its feedback.
    const renderGuessFeedback = (g) => (
        <div key={g.guessName} className="p-4 my-2 border-2 border-slate-700 rounded-lg shadow-md bg-slate-800 transition-all duration-300">
            <div className="flex flex-col sm:flex-row items-center justify-between space-y-4 sm:space-y-0 sm:space-x-4 text-white">
                <h3 className="text-xl font-bold mb-2 text-white text-center sm:text-left">{g.guessName}</h3>
                
                <div className="flex items-center space-x-2">
                    <div className={`p-4 rounded-lg flex-1 text-center font-bold text-xl ${g.feedback?.team_match || g.correct ? 'bg-green-500' : 'bg-red-500'}`}>
                        {g.feedback?.guessed_team}
                    </div>
                    <div className={`p-4 rounded-lg flex-1 text-center font-bold text-xl ${g.feedback?.position_match || g.correct ? 'bg-green-500' : 'bg-red-500'}`}>
                        {g.feedback?.guessed_position}
                    </div>
                    <div className={`p-4 rounded-lg flex-1 text-center font-bold text-xl ${g.feedback?.jersey_match || g.correct ? 'bg-green-500' : 'bg-red-500'}`}>
                        {g.feedback?.guessed_jersey}
                        {g.feedback?.jersey_hint === 'up' && ' ▲'}
                        {g.feedback?.jersey_hint === 'down' && ' ▼'}
                    </div>
                </div>
            </div>
        </div>
    );

    return (
        <div className="min-h-screen bg-slate-900 text-white font-inter p-4 flex flex-col items-center">
            <header className="text-center my-8">
                <h1 className="text-4xl sm:text-5xl font-extrabold text-white tracking-tight">NBA-dle</h1>
                <p className="mt-2 text-lg text-slate-400">Guess the daily NBA player!</p>
            </header>

            <main className="w-full max-w-2xl px-4">
                <section className="bg-slate-800 p-6 rounded-xl shadow-lg border-2 border-slate-700">
                    <h2 className="text-2xl font-bold mb-4 text-white">How to Play</h2>
                    <p className="text-slate-300">
                        Guess the NBA player in as few tries as possible. You get three clues: their team, position, and jersey number. After each guess, you'll see how close you are. A red cross means the clue is incorrect. A green checkmark means it's a match! For jersey numbers, you'll get a hint if your guess is too high or too low.
                    </p>
                </section>

                <section className="mt-8 bg-slate-800 p-6 rounded-xl shadow-lg border-2 border-slate-700">
                    <h2 className="text-2xl font-bold mb-4 text-white">Clues</h2>
                    <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 text-center">
                        <div className="p-4 bg-slate-700 rounded-lg shadow-inner">
                            <h3 className="font-bold text-slate-400">Team</h3>
                            <p className="text-white mt-1 text-xl">{guessCount >= 5 ? clues.team_name || 'Loading...' : '???'}</p>
                        </div>
                        <div className="p-4 bg-slate-700 rounded-lg shadow-inner">
                            <h3 className="font-bold text-slate-400">Position</h3>
                            <p className="text-white mt-1 text-xl">{guessCount >= 10 ? clues.position || 'Loading...' : '???'}</p>
                        </div>
                        <div className="p-4 bg-slate-700 rounded-lg shadow-inner">
                            <h3 className="font-bold text-slate-400">Jersey</h3>
                            <p className="text-white mt-1 text-xl">{guessCount >= 15 ? clues.jersey || 'Loading...' : '???'}</p>
                        </div>
                    </div>
                </section>

                <section className="mt-8">
                    {isPlayerFound ? (
                        <div className="text-center p-6 bg-green-500 text-white rounded-lg shadow-lg font-bold text-xl transition-all duration-300 transform scale-105">
                            Congratulations! You found the player in {guesses.length} guesses.
                        </div>
                    ) : (
                        <form onSubmit={handleGuessSubmit} className="relative flex flex-col sm:flex-row gap-4">
                            <input
                                type="text"
                                value={guess}
                                onChange={handleInputChange}
                                className="flex-1 p-3 rounded-lg bg-slate-700 text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-blue-500 border border-transparent focus:border-blue-500 transition-all duration-300"
                                placeholder="Enter your guess..."
                                disabled={isLoading}
                            />
                            {filteredPlayers.length > 0 && (
                                <ul className="absolute top-14 w-full bg-slate-800 border border-slate-700 rounded-lg shadow-lg z-10 max-h-60 overflow-y-auto">
                                    {filteredPlayers.map(player => (
                                        <li
                                            key={player.id}
                                            onClick={() => handlePlayerSelect(player.full_name)}
                                            className="p-3 hover:bg-slate-700 cursor-pointer transition-colors duration-200"
                                        >
                                            {player.full_name}
                                        </li>
                                    ))}
                                </ul>
                            )}
                            <button
                                type="submit"
                                className="bg-blue-600 text-white font-bold py-3 px-6 rounded-lg shadow-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 focus:ring-offset-slate-900 transition-all duration-300"
                                disabled={isLoading}
                            >
                                {isLoading ? 'Checking...' : 'Submit Guess'}
                            </button>
                        </form>
                    )}
                </section>

                {message && (
                    <div className={`mt-4 text-center p-3 rounded-lg shadow-md font-medium ${isPlayerFound ? 'bg-green-500 text-white' : 'bg-red-500 text-white'}`}>
                        {message}
                    </div>
                )}

                <section className="mt-8">
                    {guesses.length > 0 && (
                        <div className="bg-slate-800 p-6 rounded-xl shadow-lg border-2 border-slate-700">
                            <h2 className="text-2xl font-bold mb-4 text-white">Your Guesses</h2>
                            <div className="space-y-4">
                                {guesses.map(renderGuessFeedback)}
                            </div>
                        </div>
                    )}
                </section>
            </main>
        </div>
    );
};

export default App;
