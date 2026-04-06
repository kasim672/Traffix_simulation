# simulation.py Documentation

## File Purpose
Owns top-level simulation state, updates traffic each frame, handles spawning, and computes per-vehicle neighbor relationships.

## Classes And Functions In This File

### class Simulation

#### __init__()
- Creates vehicle list, signal object, control states, spawn timers, and metrics.

#### toggle_pause()
- Toggles paused state.

#### increase_speed()
- Increases simulation speed multiplier within configured bounds.

#### decrease_speed()
- Decreases simulation speed multiplier within configured bounds.

#### trigger_ambulance()
- Starts emergency mode and spawns an ambulance when possible.

#### _choose_ambulance_direction()
- Picks a clear entry direction with low traffic count.

#### set_signal_green(direction)
- Forwards manual signal request to `TrafficSignal`.

#### set_signal_auto(enabled)
- Forwards auto/manual mode request to `TrafficSignal`.

#### update(dt)
- Main per-frame simulation update:
  - updates signal state
  - spawns traffic (unless emergency mode)
  - builds ahead map
  - updates all vehicles
  - removes off-screen vehicles
  - clears emergency mode when ambulance exits

#### _try_spawn(direction)
- Attempts vehicle spawn if edge is clear.

#### _can_spawn_direction(direction, margin_mult)
- Checks whether spawn edge has enough free space.

#### _near_spawn_edge(v, direction, margin_mult)
- Helper for spawn occupancy checks.

#### _build_ahead_map()
- Builds nearest-leading-vehicle map for each lane/direction.

#### vehicle_counts_by_direction()
- Returns active vehicle counts by direction for HUD.

## Computer Graphics Algorithms Used In This File
- Core simulation algorithm, not direct rendering.
- Uses direction-wise sorting and nearest-leader lookup (lane-order heuristic) to support believable movement.
