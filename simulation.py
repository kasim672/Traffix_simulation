# =============================================================================
#  simulation.py  –  Master simulation state: vehicles, signal, spawning
# =============================================================================

import random
from typing import Optional

from constants import (
    EAST, WEST, NORTH, SOUTH,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    VEHICLE_LENGTH, MIN_GAP,
    BASE_SPAWN_INTERVAL, SPAWN_PROBABILITY,
    MIN_SPEED_MULT, MAX_SPEED_MULT, SPEED_STEP,
)
from vehicles import Vehicle
from signals  import TrafficSignal


class Simulation:
    """
    Top-level simulation manager.

    Responsibilities
    ────────────────
    • Owns the list of active vehicles and the TrafficSignal.
    • Each frame: advances the signal, attempts vehicle spawning,
      computes the 'vehicle-ahead' map, and updates every vehicle.
    • Exposes pause / speed controls for the main loop.
    • Tracks statistics (vehicles passed, elapsed sim-time).
    """

    def __init__(self):
        self.vehicles:      list[Vehicle]  = []
        self.signal:        TrafficSignal  = TrafficSignal()
        self.emergency_active: bool = False

        # Per-direction spawn countdown timers
        self._spawn_timers: dict[int, float] = {
            EAST: 0.0, WEST: 0.0, NORTH: 0.0, SOUTH: 0.0
        }

        # Controls
        self.speed_mult:  float = 1.0
        self.paused:      bool  = False

        # Statistics
        self.vehicles_passed: int   = 0
        self.elapsed:         float = 0.0   # total elapsed simulation seconds

    # =========================================================================
    #  Public controls  (called from main loop on key events)
    # =========================================================================

    def toggle_pause(self):
        self.paused = not self.paused

    def increase_speed(self):
        self.speed_mult = min(MAX_SPEED_MULT,
                              round(self.speed_mult + SPEED_STEP, 4))

    def decrease_speed(self):
        self.speed_mult = max(MIN_SPEED_MULT,
                              round(self.speed_mult - SPEED_STEP, 4))

    def trigger_ambulance(self):
        """Spawn an ambulance and force all other traffic to yield."""
        if self.emergency_active:
            return

        direction = self._choose_ambulance_direction()
        if direction is None:
            return
        self.vehicles.append(Vehicle(direction, kind="ambulance"))
        self.emergency_active = True

    def _choose_ambulance_direction(self) -> Optional[int]:
        """Pick a clear approach; return None if all spawns are blocked."""
        candidates = [EAST, WEST, NORTH, SOUTH]
        random.shuffle(candidates)
        for direction in candidates:
            if self._can_spawn_direction(direction, margin_mult=3.0):
                return direction
        return None

    def set_signal_green(self, direction: int):
        """Manual signal control: set a single direction to GREEN."""
        self.signal.set_green(direction)

    def set_signal_auto(self, enabled: bool):
        """Enable/disable automatic signal cycling."""
        self.signal.set_auto_cycle(enabled)

    # =========================================================================
    #  Main update  (called once per frame)
    # =========================================================================

    def update(self, dt: float):
        """
        Advance the simulation by `dt` real-time seconds.
        All internal logic runs in scaled simulation-time (dt × speed_mult).
        """
        if self.paused:
            return

        dt_s = dt * self.speed_mult     # simulation-time delta
        self.elapsed += dt_s

        # 1 ── Advance the traffic signal
        self.signal.update(dt_s)

        # 2 ── Attempt vehicle spawning on each approach, unless emergency traffic is active
        if not self.emergency_active:
            for direction in (EAST, WEST, NORTH, SOUTH):
                self._spawn_timers[direction] += dt_s
                if self._spawn_timers[direction] >= BASE_SPAWN_INTERVAL:
                    self._spawn_timers[direction] -= BASE_SPAWN_INTERVAL
                    if random.random() < SPAWN_PROBABILITY:
                        self._try_spawn(direction)

        # 3 ── Build the "nearest vehicle ahead in same lane" map
        ahead_map = self._build_ahead_map()

        # 4 ── Update every vehicle
        for v in self.vehicles:
            stop  = self.signal.should_stop(v.direction)
            ahead = ahead_map.get(v.vid)
            if v.kind == "ambulance":
                nearby_same_dir = [u for u in self.vehicles if u.vid != v.vid and u.direction == v.direction]
                v.update(False, None, nearby_same_dir=nearby_same_dir)
            else:
                v.update(stop, ahead, emergency_stop=self.emergency_active)

        # 5 ── Remove vehicles that have exited the screen
        before = len(self.vehicles)
        self.vehicles = [v for v in self.vehicles if not v.is_off_screen()]
        self.vehicles_passed += before - len(self.vehicles)

        if self.emergency_active and not any(v.kind == "ambulance" for v in self.vehicles):
            self.emergency_active = False

    # =========================================================================
    #  Internal helpers
    # =========================================================================

    def _try_spawn(self, direction: int):
        """
        Spawn a new vehicle in `direction` if the spawn area is unblocked.
        We check whether any existing vehicle of the same direction is still
        close to the entry edge; if so, we skip to avoid overlapping.
        """
        if not self._can_spawn_direction(direction):
            return
        self.vehicles.append(Vehicle(direction))

    def _can_spawn_direction(self, direction: int, margin_mult: float = 2.5) -> bool:
        """True if the entry edge for `direction` is clear for spawning."""
        for v in self.vehicles:
            if v.direction == direction and self._near_spawn_edge(v, direction, margin_mult=margin_mult):
                return False
        return True

    def _near_spawn_edge(self, v: Vehicle, direction: int, margin_mult: float = 2.5) -> bool:
        """
        True if vehicle `v` is still within a couple of car-lengths of its
        spawn edge (used to prevent newly spawned vehicles from overlapping).
        """
        margin = VEHICLE_LENGTH * margin_mult + MIN_GAP
        if direction == EAST:
            return v.x < (-VEHICLE_LENGTH / 2 + margin)
        if direction == WEST:
            return v.x > (SCREEN_WIDTH + VEHICLE_LENGTH / 2 - margin)
        if direction == SOUTH:
            return v.y < (-VEHICLE_LENGTH / 2 + margin)
        # NORTH
        return v.y > (SCREEN_HEIGHT + VEHICLE_LENGTH / 2 - margin)

    def _build_ahead_map(self) -> dict[int, Optional[Vehicle]]:
        """
        For every vehicle, find the one directly ahead in the same lane.

        Algorithm
        ─────────
        Group vehicles by direction, sort so index 0 is the *most advanced*
        (furthest along the route).  For vehicle at sorted index i, the
        vehicle immediately ahead is at index i−1.

        Returns a dict mapping vehicle-ID → Vehicle-ahead (or None).
        """
        by_dir: dict[int, list[Vehicle]] = {
            EAST: [], WEST: [], NORTH: [], SOUTH: []
        }
        for v in self.vehicles:
            by_dir[v.direction].append(v)

        sort_rules = {
            EAST: (lambda v: v.x, True),
            WEST: (lambda v: v.x, False),
            SOUTH: (lambda v: v.y, True),
            NORTH: (lambda v: v.y, False),
        }

        ahead_map: dict[int, Optional[Vehicle]] = {}

        for direction, group in by_dir.items():
            # Sort so the most-advanced vehicle is first (index 0)
            key_fn, rev = sort_rules[direction]
            s = sorted(group, key=key_fn, reverse=rev)

            for i, v in enumerate(s):
                # The vehicle at index (i−1) is directly ahead; none for index 0
                ahead_map[v.vid] = s[i - 1] if i > 0 else None

        return ahead_map

