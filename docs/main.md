# main.py

## Purpose
Entry point for the simulation runtime.

This file initializes Pygame, creates core objects, handles keyboard input, and runs the frame loop.

## Key Function
### main()
Responsibilities:
- initialize window, icon, and clock,
- construct `Simulation` and `Renderer`,
- process events each frame,
- compute delta time and smooth FPS value,
- call simulation update and frame rendering,
- terminate cleanly on quit.

## Input Handling
The key handler covers:
- quitting,
- pause/resume,
- ambulance trigger,
- manual signal requests,
- automatic signal mode toggle,
- speed multiplier increase/decrease.

## Runtime Flow
Per frame:
1. process events,
2. update simulation state,
3. render frame,
4. flip display buffer.

## Notes
- This file does not contain traffic algorithms directly.
- Traffic and rendering behavior are delegated to `simulation.py` and `renderer.py`.
