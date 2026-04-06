# Real-Time Traffic Simulation

## Overview
This project is a real-time 2D traffic intersection simulator built with Python and Pygame.

It models a four-way junction with:
- one active green approach at a time,
- automatic signal cycling with a yellow transition,
- manual signal control from keyboard input,
- continuous vehicle spawning and car-following behavior,
- emergency ambulance priority behavior,
- live HUD and control overlay.

The codebase is intentionally modular so each concern is isolated:
- simulation state and update logic,
- traffic signal state machine,
- vehicle motion/spacing,
- rendering and UI overlay,
- shared constants.

## Features
- Real-time simulation loop with frame-rate-aware timing.
- Four-way intersection with procedural road drawing.
- Signal finite state machine with green and yellow-before-green phases.
- Automatic signal cycling and manual override mode.
- Vehicle spawning, stopping, and following based on spacing.
- Emergency ambulance mode with path-offset selection and safety clamp.
- Speed multiplier controls and pause support.
- HUD for status, timer, counts, and speed.

## Preview and Demo
You can watch a recorded project preview in:

- [PROJECTPREVIEWGIF.gif](PROJECTPREVIEWGIF.gif)

This demo shows the live intersection simulation, signal transitions, vehicle flow behavior, HUD updates, and emergency ambulance handling.

## Project Layout
```
traffic_sim/
|-- main.py
|-- constants.py
|-- signals.py
|-- simulation.py
|-- vehicles.py
|-- renderer.py
|-- requirements.txt
|-- README.md
`-- docs/
    |-- main.md
    |-- constants.md
    |-- signals.md
    |-- simulation.md
    |-- vehicles.md
    |-- renderer.md
    `-- requirements.md
```

## Requirements
- Python 3.9+
- pygame 2.0+

## Setup
1. Create and activate a virtual environment (recommended).
2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Run
```bash
python main.py
```

## Controls
- P: Pause or resume simulation.
- A: Trigger ambulance event.
- N / E / S / W: Request manual signal direction.
- R: Return to automatic signal cycling.
- + or Up Arrow: Increase simulation speed.
- - or Down Arrow: Decrease simulation speed.
- ESC or Q: Quit.

Speed multiplier range is configurable in constants and defaults to 0.25x through 4.00x.

## How It Works
### 1. Main Loop
`main.py` runs the application loop:
- collect input events,
- compute delta time,
- advance simulation,
- render current frame.

### 2. Simulation Update
`simulation.py` owns all runtime entities and updates in this order:
1. signal update,
2. vehicle spawn attempts,
3. nearest-leader map build,
4. per-vehicle motion update,
5. cleanup of off-screen vehicles and counters.

### 3. Signal Logic
`signals.py` implements a finite state machine:
- GREEN phase,
- YELLOW_BEFORE_GREEN transition,
- auto-cycle and manual override support.

### 4. Vehicle Logic
`vehicles.py` handles:
- acceleration and deceleration,
- stop-line braking,
- following behavior based on gap to leader,
- emergency yielding,
- ambulance side-path choice with overlap prevention.

### 5. Rendering
`renderer.py` draws in layered order (painter style):
- static road/background,
- signals,
- vehicles,
- HUD and controls,
- pause overlay.

## Architecture Summary
- `main.py`: app lifecycle and inputs.
- `constants.py`: centralized configuration.
- `signals.py`: signal state machine and signal rendering.
- `simulation.py`: world state and per-frame update orchestration.
- `vehicles.py`: per-vehicle behavior and vehicle drawing.
- `renderer.py`: scene and UI rendering.

## Graphics and Simulation Techniques
- Painter's algorithm for visual layering.
- Procedural raster drawing using primitive shapes.
- Delta-time based runtime updates.
- Direction-group sorting for nearest-leader lookup.
- Gap-based car-following heuristic.
- Smooth interpolation for speed and lateral offset.

## Documentation Guide
Detailed module-level documentation is available in the docs folder:
- docs/main.md
- docs/constants.md
- docs/signals.md
- docs/simulation.md
- docs/vehicles.md
- docs/renderer.md
- docs/requirements.md
