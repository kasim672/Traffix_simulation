# =============================================================================
#  signals.py  –  TrafficSignal: one-direction green logic + manual override
# =============================================================================

import pygame
from constants import (
    EAST, WEST, NORTH, SOUTH,
    INTER_LEFT, INTER_RIGHT, INTER_TOP, INTER_BOTTOM,
    GREEN_DURATION, YELLOW_DURATION,
    LIGHT_RED, LIGHT_YELLOW, LIGHT_GREEN, LIGHT_OFF,
    POLE_DARK, POLE_EDGE,
)


class TrafficSignal:
    """Controls a 4-way signal where only one approach is green at a time."""

    _CYCLE = [NORTH, EAST, SOUTH, WEST]

    def __init__(self):
        self._phase_idx = 0
        self.active_direction = self._CYCLE[self._phase_idx]
        self.pending_direction = self.active_direction
        self.phase = "GREEN"
        self.timer = 0.0
        self.green_duration = GREEN_DURATION
        self.yellow_duration = YELLOW_DURATION
        self.auto_cycle = True

    # =========================================================================
    #  Logic
    # =========================================================================

    def update(self, dt: float):
        """Advance signal state with YELLOW_BEFORE_GREEN transition."""
        self.timer += dt

        if self.phase == "GREEN":
            if self.auto_cycle and self.timer >= self.green_duration:
                self.timer = 0.0
                self._phase_idx = (self._phase_idx + 1) % len(self._CYCLE)
                self.pending_direction = self._CYCLE[self._phase_idx]
                self.phase = "YELLOW_BEFORE_GREEN"
        elif self.phase == "YELLOW_BEFORE_GREEN":
            if self.timer >= self.yellow_duration:
                self.timer = 0.0
                self.active_direction = self.pending_direction
                self.phase = "GREEN"

    def should_stop(self, direction: int) -> bool:
        """Return True if `direction` is currently red."""
        if self.phase != "GREEN":
            return True
        return direction != self.active_direction

    def set_green(self, direction: int):
        """Manual override: set exactly one direction to green."""
        if direction not in (EAST, WEST, SOUTH, NORTH):
            return
        self.auto_cycle = False
        if direction == self.active_direction and self.phase == "GREEN":
            self.timer = 0.0
            return

        self.timer = 0.0
        self.pending_direction = direction
        self.phase = "YELLOW_BEFORE_GREEN"
        self._phase_idx = self._CYCLE.index(direction)

    def set_auto_cycle(self, enabled: bool):
        self.auto_cycle = bool(enabled)
        if self.phase == "GREEN":
            self.timer = 0.0

    def time_remaining(self) -> float:
        if self.phase == "YELLOW_BEFORE_GREEN":
            return max(0.0, self.yellow_duration - self.timer)
        if not self.auto_cycle:
            return 0.0
        return max(0.0, self.green_duration - self.timer)

    def progress(self) -> float:
        if self.phase == "YELLOW_BEFORE_GREEN":
            return min(self.timer / self.yellow_duration, 1.0)
        if not self.auto_cycle:
            return 1.0
        return min(self.timer / self.green_duration, 1.0)

    # =========================================================================
    #  Rendering
    # =========================================================================

    def _draw_signal_box(self, surface: pygame.Surface, cx: int, cy: int, active_color: tuple):
        """Draw a 3-bulb traffic light housing centered at (cx, cy)."""
        pw, ph = 16, 42
        box = pygame.Rect(cx - pw // 2, cy - ph // 2, pw, ph)
        pygame.draw.rect(surface, POLE_DARK, box, border_radius=4)
        pygame.draw.rect(surface, POLE_EDGE, box, 1, border_radius=4)

        pole_rect = pygame.Rect(cx - 2, cy + ph // 2, 4, 12)
        pygame.draw.rect(surface, POLE_DARK, pole_rect)

        bulb_r = 4
        bulb_defs = [
            (LIGHT_RED, active_color == LIGHT_RED),
            (LIGHT_YELLOW, active_color == LIGHT_YELLOW),
            (LIGHT_GREEN, active_color == LIGHT_GREEN),
        ]
        for i, (on_col, lit) in enumerate(bulb_defs):
            bx = cx
            by = cy - ph // 2 + 8 + i * 13
            col = on_col if lit else LIGHT_OFF
            pygame.draw.circle(surface, col, (bx, by), bulb_r)
            if lit:
                glow_surf = pygame.Surface((bulb_r * 6, bulb_r * 6), pygame.SRCALPHA)
                glow_col = (*on_col[:3], 55)
                pygame.draw.circle(glow_surf, glow_col, (bulb_r * 3, bulb_r * 3), bulb_r * 3)
                surface.blit(glow_surf, (bx - bulb_r * 3, by - bulb_r * 3))

    def draw(self, surface: pygame.Surface):
        """Draw approach-specific lights near each entry of the intersection."""
        gap = 20
        posts = [
            (INTER_LEFT - gap, INTER_TOP - gap, SOUTH),   # top entry (southbound)
            (INTER_RIGHT + gap, INTER_TOP - gap, WEST),   # right entry (westbound)
            (INTER_LEFT - gap, INTER_BOTTOM + gap, EAST), # left entry (eastbound)
            (INTER_RIGHT + gap, INTER_BOTTOM + gap, NORTH), # bottom entry (northbound)
        ]
        for cx, cy, controlled_dir in posts:
            if self.phase == "YELLOW_BEFORE_GREEN" and controlled_dir == self.pending_direction:
                lamp = LIGHT_YELLOW
            elif self.phase == "GREEN" and controlled_dir == self.active_direction:
                lamp = LIGHT_GREEN
            else:
                lamp = LIGHT_RED
            self._draw_signal_box(surface, cx, cy, lamp)
