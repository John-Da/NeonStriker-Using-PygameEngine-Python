# Neon Striker

![Python](https://img.shields.io/badge/Python-3.x-blue)
![Pygame](https://img.shields.io/badge/Pygame-Game%20Engine-green)

**Neon Striker** is a fast‑paced arcade shooter built using **Python and Pygame**. The game focuses on reflex‑based gameplay, neon‑styled visuals, and score‑driven progression. Players control a Green Triangle and must survive waves of enemies while achieving the highest possible score. Enemies have different shapes (border): triangle, square, and ploygon with random color. Map is auto regenerated in each wave and game start.

https://github.com/user-attachments/assets/f2427d1b-ebd9-4314-9e95-ad2416e262fa

---

## Features

* Neon‑style arcade visual theme
* Keyboard and controller support
* Real‑time score tracking
* Increasing difficulty over time
* Lightweight single‑file game structure for easy distribution

---

## System Requirements

* Python 3.8 or later
* Pygame library installed
* Desktop operating system (Windows, macOS, Linux)

Install dependencies:

```bash
pip install pygame
```

---

## File Structure

The game is designed to run from a single Python file:

```
Neon Striker/
    neon_striker.py
```

## **Creat asset/sounds directory for all .mp3 and .wav files.**

---

## How to Run the Game

Navigate to the game directory and run:

```bash
python neon_striker.py
```

If integrated into a launcher, ensure the launcher executes the Python file using the system Python interpreter.

---

## Controls

### Keyboard

* **WASD** – Move player
* **Mouse** - Turn around
* **Left Click** – Shoot
* **Esc** – Pause menu
* **Return/Enter** - Confirm/Select

### Controller (Nintendo Switch Pro Controller)

* **Left Stick** – Move player
* **Right Stick** – Turn around (Auto shoot)
* **Plus / Start** – Pause menu
* **A/X - Confirm/Select

---

## Gameplay Mechanics

* Enemies spawn continuously with increasing speed and quantity.
* Player earns points for destroying enemies.
* Collision with enemies reduces player life.

---

## Future Improvements

* Sound effects and background music
* Power‑ups and special weapons
* Boss battles
* Online leaderboard support

---
