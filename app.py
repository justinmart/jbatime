import time
import sys
import threading
import pygame  # Ensure you have pygame installed: pip install pygame
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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
        if self.time_left < 0:
            print("{}'s time has run out!".format(self.name))
            return False
        return True

class Game:
    def __init__(self, num_players, initial_time, increment, game_title):
        self.players = [Player("Player {}".format(i+1), initial_time, increment) for i in range(num_players)]
        self.current_player = 0
        self.paused = False
        self.lock = threading.Lock()
        self.game_title = game_title
        self.total_elapsed_time = 0
        self.total_play_time = 0
        self.turn_count = 0

    def next_player(self):
        self.players[self.current_player].add_time()
        self.current_player = (self.current_player + 1) % len(self.players)
        self.turn_count += 1

    def pause(self):
        self.paused = not self.paused

    def edit_time_bank(self, player_index, new_time, new_increment):
        with self.lock:
            self.players[player_index].time_left = new_time
            self.players[player_index].increment = new_increment

    def run_game(self):
        while True:
            if not self.paused:
                start_time = time.time()
                time.sleep(1)
                elapsed = time.time() - start_time
                self.total_play_time += elapsed

                if not self.players[self.current_player].deduct_time(elapsed):
                    self.sound_alarm()
                    additional_time = 30  # Additional time to add for demonstration
                    self.players[self.current_player].time_left += additional_time

                self.next_player()

            self.total_elapsed_time += 1
            time.sleep(1)

    def sound_alarm(self):
        print("Playing sound...")
        pygame.mixer.init()
        pygame.mixer.music.load("alarm.wav")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            time.sleep(1)

game = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/start', methods=['POST'])
def start_game():
    global game
    data = request.get_json()
    game_title = data['game_title']
    num_players = int(data['num_players'])
    initial_time = int(data['initial_time'])
    increment = int(data['increment'])
    game = Game(num_players, initial_time, increment, game_title)
    threading.Thread(target=game.run_game).start()
    return jsonify(success=True)

@app.route('/status', methods=['GET'])
def get_status():
    global game
    if game:
        return jsonify({
            'game_title': game.game_title,
            'total_elapsed_time': game.total_elapsed_time,
            'total_play_time': game.total_play_time,
            'turn_count': game.turn_count,
            'players': [
                {
                    'name': player.name,
                    'total_play_time': player.total_play_time,
                    'time_left': player.time_left,
                    'time_percent': (player.total_play_time / game.total_play_time) * 100 if game.total_play_time > 0 else 0
                }
                for player in game.players
            ],
            'current_player': game.current_player,
            'paused': game.paused
        })
    return jsonify(success=False, error="Game not started")

@app.route('/control', methods=['POST'])
def control():
    global game
    data = request.get_json()
    if game:
        command = data['command']
        if command == 'pause':
            game.pause()
        elif command == 'next':
            game.next_player()
        elif command == 'edit':
            player_index = int(data['player_index'])
            new_time = int(data['new_time'])
            new_increment = int(data['new_increment'])
            game.edit_time_bank(player_index, new_time, new_increment)
        return jsonify(success=True)
    return jsonify(success=False, error="Game not started")

if __name__ == '__main__':
    app.run(debug=True)