# Real-Time Traffic Simulation & Visualization System

A fully modular 4-way intersection traffic simulator built with **Python + Pygame**.  
Vehicles spawn, queue, obey signals, and navigate the intersection with smooth collision avoidance and emergency-priority behavior.

---

## Project Structure

```
traffic_sim/
├── main.py          # Entry point – game loop and event handling
├── constants.py     # All configuration: screen size, colours, road geometry, physics
├── vehicles.py      # Vehicle class – physics, collision avoidance, rendering
├── signals.py       # TrafficSignal class – phase cycling and rendering
├── simulation.py    # Simulation class – owns all entities, drives the update loop
├── renderer.py      # Renderer class – draws roads, markings, HUD
├── requirements.txt
└── README.md
```

---

## Features

| Feature | Detail |
|---|---|
| **4-way intersection** | Wider 2D crossroads with procedural road geometry |
| **Single-direction signal logic** | Only one approach is green at a time |
| **Auto + manual signals** | Auto cycle plus manual direction override from keyboard |
| **Queue formation** | Vehicles stop behind each other with minimum safe gap |
| **Collision avoidance** | Car-following model with smooth decel/accel |
| **Random spawning** | All four approaches; density self-regulates |
| **Emergency ambulance mode** | Priority vehicle with dynamic side-path selection (left/right/center) based on available gap |
| **No-overlap ambulance safety** | Hard spacing clamp prevents unrealistic overlap while overtaking |
| **Smooth animation** | 60 FPS game loop, delta-time physics |
| **HUD** | Signal mode/state, timer, vehicle stats, speed, key bindings |

---

## Requirements

- Python 3.9+
- pygame 2.0+

---

## Installation

```bash
pip install -r requirements.txt
```

---

## Run

```bash
python main.py
```

---

## Controls

| Key | Action |
|---|---|
| `N` / `E` / `S` / `W` | Set green signal direction manually |
| `R` | Resume automatic signal cycle |
| `A` | Trigger emergency ambulance |
| `P` | Pause / Resume |
| `+` or `↑` | Speed up simulation |
| `-` or `↓` | Slow down simulation |
| `ESC` or `Q` | Quit |

Speed range: **0.25×** (slow-motion) to **4.00×** (fast-forward).

---

## Architecture

```
main.py
  └── Simulation.update(dt)
    ├── TrafficSignal.update(dt_scaled)   # advance active green direction
        ├── _try_spawn(direction)             # probabilistic vehicle creation
        ├── _build_ahead_map()                # O(n log n) lane sorting
    └── Vehicle.update(...)               # per-vehicle physics + emergency behavior

Renderer.draw_frame(sim, fps)
  ├── blit static road surface               # roads, markings, arrows
  ├── TrafficSignal.draw()                   # active approach lights
  ├── Vehicle.draw() × N                     # body, roof, windshield, lights
  └── _draw_hud()                            # semi-transparent info panel
```

### Vehicle motion model

Each vehicle has a **desired speed** (`speed`) and a **current speed** (`cur_speed`) that interpolates toward it:

- **Signal stop**: quadratic ease-in deceleration based on distance to stop line.  
  Vehicle only brakes if its *front* hasn't yet crossed the stop line, so vehicles already inside the intersection clear through unimpeded.

- **Car following**: gap-based speed matching.  
  When the gap to the vehicle ahead falls below `BRAKE_DIST`, the follower's target speed blends toward the leader's current speed proportional to the remaining gap.

- **Acceleration** / **deceleration** rates are configurable via `ACCEL_RATE` / `DECEL_RATE` in `constants.py`.

- **Emergency yielding**: during ambulance mode, non-ambulance vehicles brake and shift laterally to create a corridor.

- **Ambulance path choice**: ambulance evaluates center/left/right offsets and picks the path with the best forward gap, then follows safely in that side-path.

---

## Computer Graphics Algorithms Used

This project combines classic 2D graphics and real-time simulation techniques:

1. **Painter's Algorithm (layered draw order)**  
  Background → roads → signals → vehicles → HUD.

2. **Procedural Raster Geometry**  
  Roads, markings, crossings, lights, and vehicles are rendered from primitives (`rect`, `line`, `circle`, `polygon`) instead of sprites.

3. **Delta-Time Real-Time Loop**  
  Frame updates use elapsed time (`dt`) for smooth, frame-rate-independent motion and timing.

4. **Finite State Machine (FSM) for Signals**  
  Signal state transitions run in auto mode and can be manually overridden.

5. **Gap-Based Car-Following Heuristic**  
  Vehicles regulate speed from bumper gap and leader speed to reduce collisions.

6. **Lateral Offset Interpolation**  
  Side movement is smoothed over frames to avoid jerky lane shifts.
