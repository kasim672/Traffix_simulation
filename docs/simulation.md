# simulation.py

## Purpose
Top-level simulation manager.

This module owns runtime state and performs per-frame world updates.

## Core Class
### Simulation
Responsibilities:
- store all active vehicles,
- own one `TrafficSignal` instance,
- process pause/speed/emergency control state,
- spawn new traffic,
- update all entities,
- track metrics (elapsed time, passed vehicles).

## Public Control Methods
- `toggle_pause()`
- `increase_speed()`
- `decrease_speed()`
- `trigger_ambulance()`
- `set_signal_green(direction)`
- `set_signal_auto(enabled)`

## Main Update Pipeline
`update(dt)` performs:
1. convert wall time to simulation time using speed multiplier,
2. update signal state,
3. attempt spawning on all approaches (when allowed),
4. build nearest-leader map,
5. update each vehicle,
6. remove off-screen vehicles and update counters,
7. clear emergency state when ambulance exits.

## Internal Helpers
- `_try_spawn(direction)`: spawn guard wrapper.
- `_can_spawn_direction(direction, margin_mult)`: spawn-space check.
- `_near_spawn_edge(vehicle, direction, margin_mult)`: proximity helper.
- `_build_ahead_map()`: direction-wise sorting and nearest-leader mapping.
- `_choose_ambulance_direction()`: selects a clear approach for ambulance entry.

## Techniques Used
- Deterministic per-frame update ordering.
- Direction-group sorting for lane leadership lookup.
- Spawn blocking near entry edges to avoid overlap at creation.
