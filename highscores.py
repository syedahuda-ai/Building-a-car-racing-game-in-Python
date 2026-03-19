"""
highscores.py - Persistent high score storage using JSON
"""

import json
import os
from constants import HIGH_SCORE_FILE


class HighScoreManager:
    def __init__(self):
        self.scores = []
        self.load()

    def load(self):
        if os.path.exists(HIGH_SCORE_FILE):
            try:
                with open(HIGH_SCORE_FILE, "r") as f:
                    self.scores = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.scores = []
        else:
            self.scores = []

    def save(self):
        try:
            with open(HIGH_SCORE_FILE, "w") as f:
                json.dump(self.scores, f, indent=2)
        except IOError:
            pass

    def add_score(self, score, difficulty):
        if score <= 0:
            return
        self.scores.append({"score": score, "diff": difficulty})
        self.scores.sort(key=lambda x: x["score"], reverse=True)
        self.scores = self.scores[:10]   # keep top 10
        self.save()

    def get_best(self):
        if not self.scores:
            return 0
        return self.scores[0]["score"]

    def get_all(self):
        return self.scores
