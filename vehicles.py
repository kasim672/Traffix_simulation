# =============================================================================
#  vehicles.py  –  Vehicle class: geometry, physics, rendering
# =============================================================================

import pygame
import random
from constants import (
    EAST, WEST, NORTH, SOUTH,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    EASTBOUND_Y, WESTBOUND_Y, SOUTHBOUND_X, NORTHBOUND_X,
    INTER_LEFT, INTER_RIGHT, INTER_TOP, INTER_BOTTOM,
    VEHICLE_LENGTH, VEHICLE_WIDTH,
    BASE_SPEED, BRAKE_DIST, MIN_GAP, ACCEL_RATE, DECEL_RATE,
    AMBULANCE_BODY, AMBULANCE_STRIPE,
    AMBULANCE_LIGHT_RED, AMBULANCE_LIGHT_BLUE,
)

# Car body colours – varied palette so vehicles are visually distinct
_CAR_COLORS = [
    (210,  68,  68),   # tomato red
    (68,  112, 215),   # cornflower blue
    (68,  195, 105),   # emerald
    (225, 182,  50),   # amber
    (175,  75, 210),   # violet
    (55,  198, 205),   # teal
    (238, 128,  48),   # orange
    (200, 200, 205),   # silver
    (58,   78, 172),   # navy
    (182,  58, 100),   # crimson
    (155, 195,  55),   # lime
    (215, 145, 185),   # pink
]

# Unique ID counter (class-level)
_next_id = 0


def _new_id() -> int:
    global _next_id
    _next_id += 1
    return _next_id


class Vehicle:
    """
    A single vehicle travelling in one direction through the intersection.

    Attributes
    ----------
    vid       : unique integer ID
    direction : one of EAST / WEST / SOUTH / NORTH
    x, y      : centre position (pixels)
    speed     : desired cruising speed (px/frame)
    cur_speed : actual current speed (px/frame, smoothly interpolated)
    color     : RGB body colour
    """

    def __init__(self, direction: int, kind: str = "car"):
        self.vid       = _new_id()
        self.direction = direction
        self.kind      = kind
        if kind == "ambulance":
            self.color = AMBULANCE_BODY
            self.speed  = BASE_SPEED * 1.8
        else:
            self.color = random.choice(_CAR_COLORS)
            # Small per-vehicle speed variation keeps traffic interesting
            self.speed = BASE_SPEED * random.uniform(0.88, 1.18)
        self.cur_speed = 0.0           # accelerate from rest at spawn edge
        self.length    = VEHICLE_LENGTH
        self.width     = VEHICLE_WIDTH
        self.lane_offset = 0.0
        self._target_lane_offset = 0.0

        # ── Spawn at the appropriate screen edge ──────────────────────────────
        if direction == EAST:
            self.x, self.y = -self.length / 2,              EASTBOUND_Y
        elif direction == WEST:
            self.x, self.y = SCREEN_WIDTH + self.length / 2, WESTBOUND_Y
        elif direction == SOUTH:
            self.x, self.y = SOUTHBOUND_X,                  -self.length / 2
        else:  # NORTH
            self.x, self.y = NORTHBOUND_X,                   SCREEN_HEIGHT + self.length / 2

    # =========================================================================
    #  Geometry helpers
    # =========================================================================

    def _lane_center(self) -> float:
        if self.direction == EAST:
            return EASTBOUND_Y
        if self.direction == WEST:
            return WESTBOUND_Y
        if self.direction == SOUTH:
            return SOUTHBOUND_X
        return NORTHBOUND_X

    def _yield_side_sign(self) -> int:
        """Direction-specific shoulder side for temporary yielding/overtake offset."""
        if self.direction == EAST:
            return 1
        if self.direction == WEST:
            return -1
        if self.direction == SOUTH:
            return -1
        return 1

    def front(self) -> float:
        """Leading-edge coordinate in the direction of travel."""
        if self.direction == EAST:  return self.x + self.length / 2
        if self.direction == WEST:  return self.x - self.length / 2
        if self.direction == SOUTH: return self.y + self.length / 2
        return                             self.y - self.length / 2   # NORTH

    def rear(self) -> float:
        """Trailing-edge coordinate."""
        if self.direction == EAST:  return self.x - self.length / 2
        if self.direction == WEST:  return self.x + self.length / 2
        if self.direction == SOUTH: return self.y - self.length / 2
        return                             self.y + self.length / 2   # NORTH

    def dist_to_stop_line(self) -> float:
        """
        Signed distance between this vehicle's front and its stop line.
          > 0  →  approaching (has NOT yet crossed the line)
          < 0  →  past the line (inside or through intersection)
        """
        if self.direction == EAST:  return INTER_LEFT   - self.front()
        if self.direction == WEST:  return self.front() - INTER_RIGHT
        if self.direction == SOUTH: return INTER_TOP    - self.front()
        return                             self.front() - INTER_BOTTOM   # NORTH

    def gap_to_ahead(self, ahead: "Vehicle") -> float:
        """
        Bumper-to-bumper gap between this vehicle's front and `ahead`'s rear.
        Positive = clear space; zero or negative = overlapping (should not happen).
        """
        if self.direction == EAST:  return ahead.rear()  - self.front()
        if self.direction == WEST:  return self.front()  - ahead.rear()
        if self.direction == SOUTH: return ahead.rear()  - self.front()
        return                             self.front()  - ahead.rear()   # NORTH

    def is_off_screen(self) -> bool:
        """True once the vehicle has completely left the visible area."""
        pad = self.length + 10
        if self.direction == EAST:  return self.x - pad > SCREEN_WIDTH
        if self.direction == WEST:  return self.x + pad < 0
        if self.direction == SOUTH: return self.y - pad > SCREEN_HEIGHT
        return                             self.y + pad < 0   # NORTH

    # =========================================================================
    #  Physics update (called once per frame)
    # =========================================================================

    def update(
        self,
        stop_for_signal: bool,
        ahead: "Vehicle | None",
        emergency_stop: bool = False,
        nearby_same_dir: "list[Vehicle] | None" = None,
    ):
        """
        Advance this vehicle by one simulation frame.

        Parameters
        ----------
        stop_for_signal : True when this direction's signal is red or yellow.
        ahead           : The nearest vehicle directly ahead in the same lane,
                          or None if the lane is clear.
        emergency_stop  : True when traffic should yield to an active ambulance.
        """
        if self.kind == "ambulance":
            target = self.speed
            self._target_lane_offset = 0.0
            if nearby_same_dir is None:
                nearby_same_dir = []

            shoulder = self.width * 0.78
            options = [0.0, -shoulder, shoulder]
            best_offset = 0.0
            best_gap = -1e9

            for cand in options:
                lane_y_or_x = self._lane_center() + cand
                nearest_ahead_gap = float("inf")
                blocked_here = False

                for other in nearby_same_dir:
                    if self.direction in (EAST, WEST):
                        lateral_sep = abs(other.y - lane_y_or_x)
                    else:
                        lateral_sep = abs(other.x - lane_y_or_x)

                    if lateral_sep > self.width * 0.85:
                        continue

                    gap = self.gap_to_ahead(other)
                    if gap <= MIN_GAP * 0.7:
                        blocked_here = True
                    if gap > 0:
                        nearest_ahead_gap = min(nearest_ahead_gap, gap)

                score = nearest_ahead_gap if nearest_ahead_gap != float("inf") else BRAKE_DIST * 3
                if blocked_here:
                    score -= BRAKE_DIST * 2
                # Keep current side unless a clearly better gap is available.
                score -= abs(cand - self.lane_offset) * 0.2

                if score > best_gap:
                    best_gap = score
                    best_offset = cand

            self._target_lane_offset = best_offset

            # Determine a leading vehicle in the chosen side-path and follow safely.
            side_leader = None
            side_leader_gap = float("inf")
            lane_y_or_x = self._lane_center() + self._target_lane_offset
            for other in nearby_same_dir:
                if self.direction in (EAST, WEST):
                    lateral_sep = abs(other.y - lane_y_or_x)
                else:
                    lateral_sep = abs(other.x - lane_y_or_x)
                if lateral_sep > self.width * 0.85:
                    continue

                gap = self.gap_to_ahead(other)
                if 0 < gap < side_leader_gap:
                    side_leader_gap = gap
                    side_leader = other

            if side_leader is not None:
                gap = side_leader_gap
                if gap <= MIN_GAP:
                    target = min(target, max(0.0, side_leader.cur_speed - 0.20))
                elif gap < BRAKE_DIST * 1.1:
                    ratio = (gap - MIN_GAP) / (BRAKE_DIST * 1.1 - MIN_GAP)
                    follow_speed = side_leader.cur_speed + ratio * (self.speed - side_leader.cur_speed)
                    target = min(target, follow_speed)
        elif emergency_stop:
            target = 0.0
            # Pull slightly to the side while yielding to ambulance
            self._target_lane_offset = self._yield_side_sign() * (self.width * 0.40)
        else:
            target = self.speed   # desired speed this frame
            self._target_lane_offset = 0.0

            # ── 1. Signal stopping ────────────────────────────────────────────
            if stop_for_signal:
                d = self.dist_to_stop_line()
                if d > 0:   # only brake if we haven't crossed the stop line yet
                    # Quadratic ease: smooth decel as vehicle approaches stop
                    ratio  = min(d / BRAKE_DIST, 1.0)
                    target = self.speed * ratio * ratio
                    if d < MIN_GAP:
                        target = 0.0   # fully stopped at the line

            # ── 2. Car-following / collision avoidance ───────────────────────
            if ahead is not None:
                gap = self.gap_to_ahead(ahead)
                if gap <= MIN_GAP:
                    target = 0.0   # stop: too close
                elif gap < BRAKE_DIST:
                    # Blend toward the leading vehicle's speed as gap shrinks
                    ratio        = (gap - MIN_GAP) / (BRAKE_DIST - MIN_GAP)
                    follow_speed = ahead.cur_speed + ratio * (self.speed - ahead.cur_speed)
                    target = min(target, follow_speed)

        # ── 3. Smooth speed interpolation ────────────────────────────────────
        if self.cur_speed < target:
            self.cur_speed = min(target, self.cur_speed + ACCEL_RATE)
        elif self.cur_speed > target:
            self.cur_speed = max(target, self.cur_speed - DECEL_RATE)

        # Per-frame smooth lane-offset interpolation
        shift_rate = 0.9
        if self.lane_offset < self._target_lane_offset:
            self.lane_offset = min(self._target_lane_offset, self.lane_offset + shift_rate)
        elif self.lane_offset > self._target_lane_offset:
            self.lane_offset = max(self._target_lane_offset, self.lane_offset - shift_rate)

        # ── 4. Position update ────────────────────────────────────────────────
        if   self.direction == EAST:  self.x += self.cur_speed
        elif self.direction == WEST:  self.x -= self.cur_speed
        elif self.direction == SOUTH: self.y += self.cur_speed
        else:                         self.y -= self.cur_speed   # NORTH

        # Apply lane offset on the perpendicular axis.
        if self.direction in (EAST, WEST):
            self.y = self._lane_center() + self.lane_offset
        else:
            self.x = self._lane_center() + self.lane_offset

        # Hard safety clamp for ambulance: never overlap a nearby vehicle ahead.
        if self.kind == "ambulance" and nearby_same_dir:
            lane_y_or_x = self._lane_center() + self.lane_offset
            for other in nearby_same_dir:
                if self.direction in (EAST, WEST):
                    lateral_sep = abs(other.y - lane_y_or_x)
                else:
                    lateral_sep = abs(other.x - lane_y_or_x)
                if lateral_sep > self.width * 0.90:
                    continue

                gap = self.gap_to_ahead(other)
                if gap < MIN_GAP:
                    pull_back = (MIN_GAP - gap)
                    if self.direction == EAST:
                        self.x -= pull_back
                    elif self.direction == WEST:
                        self.x += pull_back
                    elif self.direction == SOUTH:
                        self.y -= pull_back
                    else:
                        self.y += pull_back
                    self.cur_speed = min(self.cur_speed, max(0.0, other.cur_speed))

    # =========================================================================
    #  Rendering
    # =========================================================================

    def draw(self, surface: pygame.Surface):
        """Draw the vehicle as a detailed coloured rectangle."""
        horizontal = self.direction in (EAST, WEST)

        # Bounding box (width × height depends on orientation)
        if horizontal:
            bw, bh = self.length, self.width
        else:
            bw, bh = self.width, self.length

        rx = int(self.x - bw / 2)
        ry = int(self.y - bh / 2)
        body = pygame.Rect(rx, ry, bw, bh)

        # ── Body fill ─────────────────────────────────────────────────────────
        pygame.draw.rect(surface, self.color, body, border_radius=5)
        if self.kind == "ambulance":
            if horizontal:
                stripe = pygame.Rect(rx + 6, ry + 3, bw - 12, bh - 6)
            else:
                stripe = pygame.Rect(rx + 3, ry + 6, bw - 6, bh - 12)
            pygame.draw.rect(surface, AMBULANCE_STRIPE, stripe, border_radius=3)

        # ── Roof (slightly darker inset) ──────────────────────────────────────
        ri = 5   # inset
        if horizontal:
            roof = pygame.Rect(rx + ri, ry + 3, bw - ri * 2, bh - 6)
        else:
            roof = pygame.Rect(rx + 3, ry + ri, bw - 6, bh - ri * 2)
        roof_col = tuple(max(0, c - 45) for c in self.color)
        pygame.draw.rect(surface, roof_col, roof, border_radius=3)

        # ── Windshield (light-blue tinted glass) ──────────────────────────────
        ws_col = (165, 210, 248)
        ws_i   = 3   # inset
        if self.direction == EAST:
            ws = pygame.Rect(rx + bw - 11, ry + ws_i, 9, bh - ws_i * 2)
        elif self.direction == WEST:
            ws = pygame.Rect(rx + 2,       ry + ws_i, 9, bh - ws_i * 2)
        elif self.direction == SOUTH:
            ws = pygame.Rect(rx + ws_i, ry + bh - 11, bw - ws_i * 2, 9)
        else:  # NORTH
            ws = pygame.Rect(rx + ws_i, ry + 2,       bw - ws_i * 2, 9)
        pygame.draw.rect(surface, ws_col, ws, border_radius=2)

        if self.kind == "ambulance":
            lightbar_w = 14 if horizontal else 10
            lightbar_h = 8 if horizontal else 14
            if horizontal:
                lightbar = pygame.Rect(int(rx + bw / 2 - lightbar_w / 2), ry + 2, lightbar_w, lightbar_h)
            else:
                lightbar = pygame.Rect(rx + 2, int(ry + bh / 2 - lightbar_h / 2), lightbar_w, lightbar_h)
            pygame.draw.rect(surface, (25, 25, 30), lightbar, border_radius=2)
            pygame.draw.rect(surface, AMBULANCE_LIGHT_RED,
                             (lightbar.x + 1, lightbar.y + 1, lightbar.w // 2 - 1, lightbar.h - 2), border_radius=2)
            pygame.draw.rect(surface, AMBULANCE_LIGHT_BLUE,
                             (lightbar.x + lightbar.w // 2, lightbar.y + 1, lightbar.w // 2 - 1, lightbar.h - 2), border_radius=2)

        # ── Headlights / tail-lights ──────────────────────────────────────────
        hl_col = (255, 255, 200)   # front: pale yellow
        tl_col = (200,  40,  40)   # rear:  red
        hl_r   = 3

        if self.direction == EAST:
            # Headlights at right end
            pygame.draw.circle(surface, hl_col, (rx + bw - 2, ry + 4),    hl_r)
            pygame.draw.circle(surface, hl_col, (rx + bw - 2, ry + bh - 4), hl_r)
            pygame.draw.circle(surface, tl_col, (rx + 2,       ry + 4),    hl_r)
            pygame.draw.circle(surface, tl_col, (rx + 2,       ry + bh - 4), hl_r)
        elif self.direction == WEST:
            pygame.draw.circle(surface, hl_col, (rx + 2,       ry + 4),    hl_r)
            pygame.draw.circle(surface, hl_col, (rx + 2,       ry + bh - 4), hl_r)
            pygame.draw.circle(surface, tl_col, (rx + bw - 2, ry + 4),    hl_r)
            pygame.draw.circle(surface, tl_col, (rx + bw - 2, ry + bh - 4), hl_r)
        elif self.direction == SOUTH:
            pygame.draw.circle(surface, hl_col, (rx + 4,      ry + bh - 2), hl_r)
            pygame.draw.circle(surface, hl_col, (rx + bw - 4, ry + bh - 2), hl_r)
            pygame.draw.circle(surface, tl_col, (rx + 4,      ry + 2),     hl_r)
            pygame.draw.circle(surface, tl_col, (rx + bw - 4, ry + 2),     hl_r)
        else:  # NORTH
            pygame.draw.circle(surface, hl_col, (rx + 4,      ry + 2),     hl_r)
            pygame.draw.circle(surface, hl_col, (rx + bw - 4, ry + 2),     hl_r)
            pygame.draw.circle(surface, tl_col, (rx + 4,      ry + bh - 2), hl_r)
            pygame.draw.circle(surface, tl_col, (rx + bw - 4, ry + bh - 2), hl_r)

        # ── Outline ───────────────────────────────────────────────────────────
        pygame.draw.rect(surface, (18, 18, 22), body, 1, border_radius=5)
