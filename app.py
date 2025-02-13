<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Game Timer</title>
    <style>
        body {
            text-align: center;
            font-family: Arial, sans-serif;
        }
        .player {
            display: inline-block;
            margin: 10px;
            padding: 10px;
            border: 1px solid black;
        }
        .current-turn {
            background-color: rgba(255, 255, 0, 0.5);
        }
    </style>
</head>
<body>
    <div id="game-setup">
        <h1>Game Setup</h1>
        <form id="setup-form">
            <label for="game-title">Game Title:</label>
            <input type="text" id="game-title" name="game-title" required><br><br>
            <label for="num-players">Number of Players:</label>
            <input type="number" id="num-players" name="num-players" min="1" required><br><br>
            <label for="initial-time">Initial Time (seconds):</label>
            <input type="number" id="initial-time" name="initial-time" min="1" required><br><br>
            <label for="increment">Increment Time (seconds):</label>
            <input type="number" id="increment" name="increment" min="1" required><br><br>
            <button type="submit">Start Game</button>
        </form>
    </div>

    <div id="game-display" style="display:none;">
        <h1 id="game-title">Dune Imperium Game Night!</h1>
        <h2>Total Elapsed Time: <span id="total-elapsed-time">0:00</span></h2>
        <h2>Total Play Time: <span id="total-play-time">0:00</span></h2>
        <h3>Turn Counter: <span id="turn-counter">0</span></h3>
        <div id="players"></div>
    </div>

    <script>
        let gameStarted = false;

        document.getElementById('setup-form').addEventListener('submit', async function(event) {
            event.preventDefault();
            const gameTitle = document.getElementById('game-title').value;
            const numPlayers = document.getElementById('num-players').value;
            const initialTime = document.getElementById('initial-time').value;
            const increment = document.getElementById('increment').value;

            const response = await fetch('/start', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    game_title: gameTitle,
                    num_players: numPlayers,
                    initial_time: initialTime,
                    increment: increment
                })
            });
            const data = await response.json();
            if (data.success) {
                gameStarted = true;
                document.getElementById('game-setup').style.display = 'none';
                document.getElementById('game-display').style.display = 'block';
                document.getElementById('game-title').innerText = gameTitle;
                fetchStatus();
            }
        });

        async function fetchStatus() {
            const response = await fetch('/status');
            const data = await response.json();
            if (data.success !== false) {
                document.getElementById('total-elapsed-time').innerText = formatTime(data.total_elapsed_time);
                document.getElementById('total-play-time').innerText = formatTime(data.total_play_time);
                document.getElementById('turn-counter').innerText = data.turn_count;

                const playersDiv = document.getElementById('players');
                playersDiv.innerHTML = '';
                data.players.forEach((player, index) => {
                    const playerDiv = document.createElement('div');
                    playerDiv.className = 'player' + (index === data.current_player ? ' current-turn' : '');
                    playerDiv.innerHTML = `
                        <h4>${player.name}</h4>
                        <p>Total Play Time: ${formatTime(player.total_play_time)}</p>
                        <p>Time Bank: ${formatTime(player.time_left)}</p>
                        <p>Time %: ${player.time_percent.toFixed(2)}%</p>
                    `;
                    playersDiv.appendChild(playerDiv);
                });
            }
        }

        function formatTime(seconds) {
            const min = Math.floor(seconds / 60);
            const sec = seconds % 60;
            return `${min}:${sec < 10 ? '0' : ''}${sec}`;
        }

        async function sendControl(command, player_index=null, new_time=null, new_increment=null) {
            const response = await fetch('/control', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({command, player_index, new_time, new_increment})
            });
            const data = await response.json();
            if (data.success !== false) {
                fetchStatus();
            }
        }

        document.addEventListener('keydown', (event) => {
            if (!gameStarted) return;
            if (event.key === ' ') {
                sendControl('next');
            } else if (event.key === 'p') {
                sendControl('pause');
            } else if (event.key === 'e') {
                const player_index = prompt("Enter the player number to edit (1-2):") - 1;
                const new_time = parseInt(prompt(`Enter new time for Player ${player_index + 1}:`));
                const new_increment = parseInt(prompt(`Enter new increment for Player ${player_index + 1}:`));
                sendControl('edit', player_index, new_time, new_increment);
            }
        });

        setInterval(fetchStatus, 1000);
    </script>
</body>
</html>
