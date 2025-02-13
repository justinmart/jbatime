# app.py

import os
import datetime
import threading
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

game = None

class Player:
    def __init__(self, name, initial_time, increment):
        self.name = name
        self.time_left = initial_time
        self.increment = increment
        self.total_play_time = 0

    def add_time(self):
        self.time_left += self.increment

    def deduct_time(self, elapsed):
        self.time_left -= elapsed
        self.total_play_time += elapsed
        return self.time_left > 0

class Game:
    def __init__(self, player_names, initial_time, increment, game_title):
        self.players = [Player(name, initial_time, increment) for name in player_names]
        self.current_player = 0
        self.paused = True
        self.lock = threading.Lock()
        self.game_title = game_title
        self.total_elapsed_time = datetime.timedelta()
        self.total_play_time = datetime.timedelta()
        self.start_time = None
        self.current_turn_start = None

    def next_player(self):
        with self.lock:
            self.players[self.current_player].add_time()
            self.current_player = (self.current_player + 1) % len(self.players)
            self.paused = True

    def pause(self):
        with self.lock:
            self.paused = not self.paused
            if not self.paused:
                self.current_turn_start = datetime.datetime.now()

    def run_game(self):
        self.start_time = datetime.datetime.now()
        while True:
            with self.lock:
                self.total_elapsed_time = datetime.datetime.now() - self.start_time
                if not self.paused:
                    elapsed = datetime.datetime.now() - self.current_turn_start
                    self.total_play_time += elapsed
                    self.current_turn_start = datetime.datetime.now()
                    if not self.players[self.current_player].deduct_time(elapsed.total_seconds()):
                        print(f"{self.players[self.current_player].name}'s time has run out!")
                        self.next_player()
            time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_game():
    global game
    data = request.get_json()
    game = Game(data['player_names'], int(data['initial_time']), int(data['increment']), data['game_title'])
    game_thread = threading.Thread(target=game.run_game)
    game_thread.daemon = True
    game_thread.start()
    return jsonify(success=True)

@app.route('/status', methods=['GET'])
def get_status():
    global game
    if game is None:
        return jsonify(success=False, error="Game not started")
    return jsonify({
        'game_title': game.game_title,
        'total_elapsed_time': str(game.total_elapsed_time),
        'total_play_time': str(game.total_play_time),
        'players': [
            {'name': player.name, 'total_play_time': str(player.total_play_time), 'time_left': player.time_left}
            for player in game.players
        ],
        'current_player': game.current_player,
        'paused': game.paused
    })

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
