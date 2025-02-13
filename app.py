import os
import time
import threading
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
            print(f"{self.name}'s time has run out!")
            return False
        return True

class Game:
    def __init__(self, player_names, initial_time, increment, game_title):
        self.players = [Player(name, initial_time, increment) for name in player_names]
        self.current_player = 0
        self.paused = True
        self.lock = threading.Lock()
        self.game_title = game_title
        self.total_elapsed_time = 0
        self.total_play_time = 0
        self.turn_count = 0

    def next_player(self):
        self.players[self.current_player].add_time()
        self.current_player = (self.current_player + 1) % len(self.players)
        self.turn_count += 1
        self.paused = True

    def pause(self):
        self.paused = not self.paused

    def edit_time_bank(self, player_index, new_time, new_increment):
        with self.lock:
            self.players[player_index].time_left = new_time
            self.players[player_index].increment = new_increment

    def run_game(self):
        while True:
            if not self.paused:
                start
