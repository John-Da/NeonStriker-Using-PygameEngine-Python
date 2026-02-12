# Neon Striker – Game Documentation

## 1. Overview

**Neon Striker** is a fast‑paced arcade shooter built using **Python and Pygame**. The game focuses on reflex‑based gameplay, neon‑styled visuals, and score‑driven progression. Players control a spaceship and must survive waves of enemies while achieving the highest possible score.

---

## 2. Features

* Neon‑style arcade visual theme
* Keyboard and controller support
* Real‑time score tracking
* Increasing difficulty over time
* Lightweight single‑file game structure for easy distribution

---

## 3. System Requirements

* Python 3.8 or later
* Pygame library installed
* Desktop operating system (Windows, macOS, Linux)

Install dependencies:

```bash
pip install pygame
```

---

## 4. File Structure

The game is designed to run from a single Python file:

```
Neon Striker/
    neon_striker.py
```

## **Creat asset/sounds directory for all .mp3 and .wav files.**

---

## 5. How to Run the Game

Navigate to the game directory and run:

```bash
python neon_striker.py
```

If integrated into a launcher, ensure the launcher executes the Python file using the system Python interpreter.

---

## 6. Controls

### Keyboard

* **Arrow Keys / WASD** – Move player
* **Space** – Shoot
* **Esc** – Pause / Exit to launcher

### Controller (Nintendo Switch Pro Controller)

* **Left Stick / D‑Pad** – Move player
* **A / B** – Shoot
* **Plus / Start** – Pause menu

---

## 7. Gameplay Mechanics

* Enemies spawn continuously with increasing speed and quantity.
* Player earns points for destroying enemies.
* Collision with enemies or projectiles reduces player life.
* The game ends when all lives are lost.

---

## Future Improvements

* Sound effects and background music
* Power‑ups and special weapons
* Boss battles
* Online leaderboard support

---
