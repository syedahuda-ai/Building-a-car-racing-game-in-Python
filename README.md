# 🏎️ TURBO RACE 3D — Python Car Racing Game

A fully featured pseudo-3D car racing game built with **Python** and **Pygame**.

![Python](https://img.shields.io/badge/Python-3.8+-blue?logo=python)
![Pygame](https://img.shields.io/badge/Pygame-2.x-green?logo=pygame)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🎮 Features

- **Pseudo-3D perspective road** with vanishing point and camera curves
- **3 Difficulty Levels** — Easy, Medium, Hard (with score multipliers)
- **Animated player car** with tilt, headlights, tail lights, and speed glow
- **Enemy cars** that scale realistically in 3D perspective
- **Overtake combo system** — chain overtakes for bonus points
- **Crash & lives system** — 3 lives per game with crash effects
- **Particle effects** — dust trails, crash explosions, sparks
- **Procedural scenery** — trees, clouds, animated grass
- **HUD** — speedometer, score, lives, difficulty badge
- **Persistent High Scores** saved to `highscores.json`
- **Full GUI** — Main menu, difficulty screen, pause, game over, leaderboard

---

## 📁 File Structure

```
car_racing_game/
├── main.py          ← Entry point — run this!
├── game.py          ← Central game loop & state machine
├── road.py          ← Pseudo-3D road rendering & perspective projection
├── player.py        ← Player car (input, physics, drawing)
├── enemy.py         ← Enemy cars (3D-scaled rendering)
├── hud.py           ← HUD: speedometer, score, lives
├── ui.py            ← All menu screens (menu, difficulty, pause, game over)
├── particles.py     ← Particle effects system
├── highscores.py    ← JSON high score persistence
├── constants.py     ← All constants and configuration
├── highscores.json  ← Auto-created on first run
└── README.md
```

---

## 🚀 Installation & Running

### 1. Prerequisites
- Python 3.8 or higher
- pip

### 2. Install Pygame
```bash
pip install pygame
```

### 3. Run the Game
```bash
cd car_racing_game
python main.py
```

---

## 🕹️ Controls

| Key               | Action            |
|-------------------|-------------------|
| `↑` / `W`         | Accelerate        |
| `↓` / `S`         | Brake             |
| `←` / `A`         | Steer left        |
| `→` / `D`         | Steer right       |
| `ESC`             | Pause / Back      |
| Mouse click       | Navigate menus    |

---

## 🏆 Difficulty Levels

| Difficulty | Enemy Speed | Curve Strength | Score Multiplier |
|------------|-------------|----------------|-----------------|
| EASY       | Slow        | Gentle         | 1×              |
| MEDIUM     | Fast        | Moderate       | 2×              |
| HARD       | Very fast   | Wild           | 3×              |

---

## 📐 Architecture Overview

```
main.py
  └─ Game (game.py)
       ├─ Road          — 3D perspective strip rendering, curve system
       ├─ PlayerCar     — physics, input, collision, drawing
       ├─ EnemyCar[]    — depth-based 3D projection & scaled drawing
       ├─ HUD           — speedometer gauge, score, lives
       ├─ UIRenderer    — all screens (menu, pause, game over, scores)
       ├─ ParticleSystem— dust, sparks, crash explosions
       └─ HighScoreManager — JSON read/write
```

---

## 🛠️ Customization

Edit `constants.py` to tweak:
- `PLAYER_MAX_SPEED`, `PLAYER_ACCEL` — player feel
- `DIFFICULTIES` dict — enemy speed, spawn rate, curve intensity
- `ROAD_WIDTH_TOP/BOTTOM` — road shape
- `HORIZON_Y` — horizon height
- `ENEMY_COLORS` — car colour palette

---

## 📄 License

MIT License — free to use, modify, and distribute.
