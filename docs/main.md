# main.py Documentation

## File Purpose
Entry point for the application. It initializes Pygame, creates the simulation and renderer objects, processes keyboard input, advances simulation time, and draws frames.

## Functions In This File

### main()
- Initializes window, icon, clock, `Simulation`, and `Renderer`.
- Runs the main real-time loop.
- Handles keyboard controls:
  - Pause/resume
  - Emergency ambulance
  - Manual signal direction selection
  - Auto signal mode
  - Speed up / speed down
  - Quit
- Calls `sim.update(dt)` and `renderer.draw_frame(sim, fps)` every frame.

## Computer Graphics Algorithms Used In This File
- Uses a real-time game loop with delta time (`dt`) to produce frame-rate-stable animation.
- No direct geometry algorithm is implemented here; drawing is delegated to `renderer.py`.
