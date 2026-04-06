# =============================================================================
#  renderer.py  –  All visual drawing for the traffic simulation
# =============================================================================

import pygame
from constants import (
    SCREEN_WIDTH, SCREEN_HEIGHT,
    ROAD_CENTER_X, ROAD_CENTER_Y, ROAD_HALF_W,
    INTER_LEFT, INTER_RIGHT, INTER_TOP, INTER_BOTTOM, INTER_W, INTER_H,
    EASTBOUND_Y, WESTBOUND_Y, SOUTHBOUND_X, NORTHBOUND_X,
    EAST, WEST, NORTH, SOUTH, DIR_NAMES,
    GRASS, ROAD_DARK, ROAD_MID,
    LANE_MARK, STOP_LINE, SIDEWALK, CURB,
    UI_PANEL, UI_BORDER, UI_LABEL, UI_VALUE, UI_TITLE_C, UI_WARN,
    WHITE, BLACK,
    LIGHT_RED, LIGHT_YELLOW, LIGHT_GREEN,
)
from simulation import Simulation


class Renderer:
    """
    Draws all visual elements for one frame.

    Draw order (painter's algorithm):
        background → grass details → roads → road markings →
        signal posts → vehicles → HUD overlay
    """

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self._load_fonts()
        # Pre-build static surfaces that don't change frame-to-frame
        self._road_surface = self._build_road_surface()

    # =========================================================================
    #  Font loading
    # =========================================================================

    def _load_fonts(self):
        pygame.font.init()
        mono_candidates = ["Consolas", "Courier New", "DejaVu Sans Mono", None]
        self.font_sm  = pygame.font.SysFont(mono_candidates, 13)
        self.font_med = pygame.font.SysFont(mono_candidates, 17, bold=True)
        self.font_lg  = pygame.font.SysFont(mono_candidates, 30, bold=True)
        self.font_xl  = pygame.font.SysFont(mono_candidates, 44, bold=True)

    # =========================================================================
    #  Pre-built static road surface
    # =========================================================================

    def _build_road_surface(self) -> pygame.Surface:
        """
        Render the roads and all static markings onto a dedicated surface
        so the main loop can blit it in one call without recomputing geometry.
        """
        surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))

        # ── Grass background ──────────────────────────────────────────────────
        surf.fill(GRASS)

        # Subtle grass texture: slightly darker horizontal bands
        for gy in range(0, SCREEN_HEIGHT, 6):
            if gy % 12 == 0:
                pygame.draw.line(surf, (60, 95, 53),
                                 (0, gy), (SCREEN_WIDTH, gy), 1)

        # ── Sidewalk kerbs (narrow strips flanking road edges) ────────────────
        sw = 10   # sidewalk width
        h_top    = ROAD_CENTER_Y - ROAD_HALF_W
        h_bottom = ROAD_CENTER_Y + ROAD_HALF_W
        v_left   = ROAD_CENTER_X - ROAD_HALF_W
        v_right  = ROAD_CENTER_X + ROAD_HALF_W

        # Top & bottom of horizontal road
        for y_pos in (h_top - sw, h_bottom):
            pygame.draw.rect(surf, SIDEWALK, (0, y_pos, SCREEN_WIDTH, sw))
            pygame.draw.rect(surf, CURB,     (0, y_pos, SCREEN_WIDTH, 2))
        # Left & right of vertical road
        for x_pos in (v_left - sw, v_right):
            pygame.draw.rect(surf, SIDEWALK, (x_pos, 0, sw, SCREEN_HEIGHT))
            pygame.draw.rect(surf, CURB,     (x_pos, 0, 2, SCREEN_HEIGHT))

        # ── Road pavement ─────────────────────────────────────────────────────
        # Horizontal road strip
        pygame.draw.rect(surf, ROAD_DARK,
                         (0, h_top, SCREEN_WIDTH, ROAD_HALF_W * 2))
        # Vertical road strip
        pygame.draw.rect(surf, ROAD_DARK,
                         (v_left, 0, ROAD_HALF_W * 2, SCREEN_HEIGHT))
        # Intersection box (slightly lighter concrete shade)
        pygame.draw.rect(surf, ROAD_MID,
                         (INTER_LEFT, INTER_TOP, INTER_W, INTER_H))

        # ── Lane centre dashed lines ──────────────────────────────────────────
        dash_len  = 20
        dash_gap  = 14
        dash_col  = LANE_MARK
        dash_w    = 2

        # Horizontal road centre line (skip over the intersection box)
        x = 0
        while x < SCREEN_WIDTH:
            x1 = x
            x2 = min(x + dash_len, SCREEN_WIDTH)
            # Skip the intersection area
            if not (INTER_LEFT - 4 < x2 and x1 < INTER_RIGHT + 4):
                pygame.draw.line(surf, dash_col,
                                 (x1, ROAD_CENTER_Y),
                                 (x2, ROAD_CENTER_Y), dash_w)
            x += dash_len + dash_gap

        # Vertical road centre line
        y = 0
        while y < SCREEN_HEIGHT:
            y1 = y
            y2 = min(y + dash_len, SCREEN_HEIGHT)
            if not (INTER_TOP - 4 < y2 and y1 < INTER_BOTTOM + 4):
                pygame.draw.line(surf, dash_col,
                                 (ROAD_CENTER_X, y1),
                                 (ROAD_CENTER_X, y2), dash_w)
            y += dash_len + dash_gap

        # ── Stop lines (white bars at intersection entry) ─────────────────────
        sl_w = 3   # line width

        # Eastbound stop line (right side of the left road segment)
        pygame.draw.line(surf, STOP_LINE,
                         (INTER_LEFT, ROAD_CENTER_Y),
                         (INTER_LEFT, h_bottom), sl_w)
        # Westbound stop line
        pygame.draw.line(surf, STOP_LINE,
                         (INTER_RIGHT, h_top),
                         (INTER_RIGHT, ROAD_CENTER_Y), sl_w)
        # Southbound stop line
        pygame.draw.line(surf, STOP_LINE,
                         (v_left, INTER_TOP),
                         (ROAD_CENTER_X, INTER_TOP), sl_w)
        # Northbound stop line
        pygame.draw.line(surf, STOP_LINE,
                         (ROAD_CENTER_X, INTER_BOTTOM),
                         (v_right, INTER_BOTTOM), sl_w)

        # ── Zebra crossings ───────────────────────────────────────────────────
        zebra_col   = (215, 215, 215)
        zebra_strip = 5
        zebra_gap   = 5
        zebra_depth = 14  # how far from kerb-line the crossing extends

        # Top crossing (for vertical road, above intersection)
        for x_z in range(v_left, v_right, zebra_strip + zebra_gap):
            pygame.draw.rect(surf, zebra_col,
                             (x_z, INTER_TOP - zebra_depth, zebra_strip, zebra_depth))
        # Bottom crossing
        for x_z in range(v_left, v_right, zebra_strip + zebra_gap):
            pygame.draw.rect(surf, zebra_col,
                             (x_z, INTER_BOTTOM, zebra_strip, zebra_depth))
        # Left crossing
        for y_z in range(h_top, h_bottom, zebra_strip + zebra_gap):
            pygame.draw.rect(surf, zebra_col,
                             (INTER_LEFT - zebra_depth, y_z, zebra_depth, zebra_strip))
        # Right crossing
        for y_z in range(h_top, h_bottom, zebra_strip + zebra_gap):
            pygame.draw.rect(surf, zebra_col,
                             (INTER_RIGHT, y_z, zebra_depth, zebra_strip))

        # ── Road edge lines ───────────────────────────────────────────────────
        edge_col = (78, 78, 88)
        # Top of horizontal road
        pygame.draw.line(surf, edge_col, (0, h_top), (INTER_LEFT, h_top), 1)
        pygame.draw.line(surf, edge_col, (INTER_RIGHT, h_top), (SCREEN_WIDTH, h_top), 1)
        # Bottom of horizontal road
        pygame.draw.line(surf, edge_col, (0, h_bottom), (INTER_LEFT, h_bottom), 1)
        pygame.draw.line(surf, edge_col, (INTER_RIGHT, h_bottom), (SCREEN_WIDTH, h_bottom), 1)
        # Left of vertical road
        pygame.draw.line(surf, edge_col, (v_left, 0), (v_left, INTER_TOP), 1)
        pygame.draw.line(surf, edge_col, (v_left, INTER_BOTTOM), (v_left, SCREEN_HEIGHT), 1)
        # Right of vertical road
        pygame.draw.line(surf, edge_col, (v_right, 0), (v_right, INTER_TOP), 1)
        pygame.draw.line(surf, edge_col, (v_right, INTER_BOTTOM), (v_right, SCREEN_HEIGHT), 1)

        # ── Direction arrow hints on the road ─────────────────────────────────
        self._draw_arrows(surf)

        return surf

    def _draw_arrows(self, surf: pygame.Surface):
        """Draw faint direction arrows on each road arm to help readability."""
        arrow_col = (88, 90, 100)
        # Position arrows along each lane, away from the intersection
        positions = [
            # (x, y, direction)
            (ROAD_CENTER_X - 200, EASTBOUND_Y,   EAST),
            (ROAD_CENTER_X + 200, WESTBOUND_Y,   WEST),
            (SOUTHBOUND_X,        ROAD_CENTER_Y - 200, SOUTH),
            (NORTHBOUND_X,        ROAD_CENTER_Y + 200, NORTH),
        ]
        for ax, ay, d in positions:
            self._draw_single_arrow(surf, ax, ay, d, arrow_col)

    @staticmethod
    def _draw_single_arrow(surf, cx, cy, direction, color, size=10):
        """Draw a simple filled arrow at (cx, cy) pointing in direction."""
        if direction == EAST:
            pts = [(cx + size, cy), (cx - size, cy - size // 2),
                   (cx - size, cy + size // 2)]
        elif direction == WEST:
            pts = [(cx - size, cy), (cx + size, cy - size // 2),
                   (cx + size, cy + size // 2)]
        elif direction == SOUTH:
            pts = [(cx, cy + size), (cx - size // 2, cy - size),
                   (cx + size // 2, cy - size)]
        else:  # NORTH
            pts = [(cx, cy - size), (cx - size // 2, cy + size),
                   (cx + size // 2, cy + size)]
        pygame.draw.polygon(surf, color, pts)

    # =========================================================================
    #  Per-frame drawing
    # =========================================================================

    def draw_frame(self, sim: Simulation, fps: float):
        """Draw everything for one frame."""
        # 1. Static road surface (background, roads, markings)
        self.screen.blit(self._road_surface, (0, 0))

        # 2. Traffic signal posts
        sim.signal.draw(self.screen)

        # 3. Vehicles (sorted by y so overlapping looks slightly natural)
        for v in sorted(sim.vehicles, key=lambda v: v.y):
            v.draw(self.screen)

        # 4. HUD
        self._draw_hud(sim, fps)

        # 5. Pause overlay (drawn last so it covers everything)
        if sim.paused:
            self._draw_pause_overlay()

    # =========================================================================
    #  HUD / Overlay
    # =========================================================================

    def _draw_hud(self, sim: Simulation, fps: float):
        """Render the semi-transparent info panel in the top-left corner."""
        panel_w, panel_h = 255, 290
        px, py = 12, 12

        # ── Panel background ──────────────────────────────────────────────────
        panel = pygame.Surface((panel_w, panel_h), pygame.SRCALPHA)
        panel.fill((*UI_PANEL, 210))
        pygame.draw.rect(panel, (*UI_BORDER, 200),
                         (0, 0, panel_w, panel_h), 1, border_radius=8)
        self.screen.blit(panel, (px, py))

        # ── Title ─────────────────────────────────────────────────────────────
        title = self.font_med.render("TRAFFIC SIMULATION", True, UI_TITLE_C)
        self.screen.blit(title, (px + 10, py + 10))

        # Separator line
        pygame.draw.line(self.screen, (*UI_BORDER, 120),
                         (px + 8, py + 32), (px + panel_w - 8, py + 32), 1)

        # ── Signal status ─────────────────────────────────────────────────────
        active_name = DIR_NAMES.get(sim.signal.active_direction, "?")
        pending_name = DIR_NAMES.get(sim.signal.pending_direction, "?")
        mode_name = "AUTO" if sim.signal.auto_cycle else "MANUAL"
        if sim.signal.phase == "YELLOW_BEFORE_GREEN":
            state_label = f"{pending_name} YELLOW ({mode_name})"
            state_color = LIGHT_YELLOW
        else:
            state_label = f"{active_name} GREEN ({mode_name})"
            state_color = LIGHT_GREEN
        s_lbl = self.font_sm.render("SIGNAL:", True, UI_LABEL)
        s_val = self.font_sm.render(state_label, True, state_color)
        self.screen.blit(s_lbl, (px + 10, py + 40))
        self.screen.blit(s_val, (px + 80, py + 40))

        # Phase progress bar
        bar_x = px + 10
        bar_y = py + 58
        bar_w = panel_w - 20
        bar_h = 7
        pygame.draw.rect(self.screen, (40, 45, 58),
                         (bar_x, bar_y, bar_w, bar_h), border_radius=3)
        fill_w = int(bar_w * sim.signal.progress())
        if fill_w > 0:
            pygame.draw.rect(self.screen, state_color,
                             (bar_x, bar_y, fill_w, bar_h), border_radius=3)
        if sim.signal.auto_cycle:
            timer_txt = f"{sim.signal.time_remaining():.1f}s remaining"
        else:
            timer_txt = "manual hold"
        time_lbl = self.font_sm.render(timer_txt, True, UI_LABEL)
        self.screen.blit(time_lbl, (px + 10, py + 68))

        # Separator
        pygame.draw.line(self.screen, (*UI_BORDER, 80),
                         (px + 8, py + 85), (px + panel_w - 8, py + 85), 1)

        # ── Counts ────────────────────────────────────────────────────────────
        counts = sim.vehicle_counts_by_direction()
        rows = [
            ("VEHICLES ACTIVE", str(len(sim.vehicles))),
            ("VEHICLES PASSED", str(sim.vehicles_passed)),
            ("ELAPSED TIME",    f"{sim.elapsed:.0f}s"),
            ("FPS",             f"{fps:.0f}"),
        ]
        y_off = py + 93
        for label, val in rows:
            l_surf = self.font_sm.render(f"{label}:", True, UI_LABEL)
            v_surf = self.font_sm.render(val, True, UI_VALUE)
            self.screen.blit(l_surf, (px + 10, y_off))
            self.screen.blit(v_surf, (px + panel_w - 10 - v_surf.get_width(), y_off))
            y_off += 18

        emergency_label = "AMBULANCE: ACTIVE" if sim.emergency_active else "AMBULANCE: READY"
        emergency_color = UI_WARN if sim.emergency_active else UI_LABEL
        e_surf = self.font_sm.render(emergency_label, True, emergency_color)
        self.screen.blit(e_surf, (px + 10, y_off - 1))

        # ── Per-direction breakdown ───────────────────────────────────────────
        pygame.draw.line(self.screen, (*UI_BORDER, 80),
                         (px + 8, y_off + 2), (px + panel_w - 8, y_off + 2), 1)
        y_off += 8
        dir_info = [(EAST, "→ EAST"), (WEST, "← WEST"),
                    (SOUTH, "↓ SOUTH"), (NORTH, "↑ NORTH")]
        for i, (d, label) in enumerate(dir_info):
            lx = px + 10 + (i % 2) * 118
            ly = y_off + (i // 2) * 16
            d_surf = self.font_sm.render(f"{label}: {counts[d]}", True, UI_LABEL)
            self.screen.blit(d_surf, (lx, ly))

        y_off += 36

        # ── Speed control ─────────────────────────────────────────────────────
        pygame.draw.line(self.screen, (*UI_BORDER, 80),
                         (px + 8, y_off), (px + panel_w - 8, y_off), 1)
        y_off += 6

        speed_col = UI_WARN if sim.speed_mult != 1.0 else UI_VALUE
        sp_lbl = self.font_sm.render("SPEED:", True, UI_LABEL)
        sp_val = self.font_med.render(f"x{sim.speed_mult:.2f}", True, speed_col)
        self.screen.blit(sp_lbl, (px + 10, y_off))
        self.screen.blit(sp_val, (px + 70, y_off - 2))

        # Speed bar
        bar_y2 = y_off + 18
        max_m   = 4.0
        pygame.draw.rect(self.screen, (40, 45, 58),
                         (px + 10, bar_y2, bar_w, 6), border_radius=3)
        sp_fill = int(bar_w * (sim.speed_mult / max_m))
        if sp_fill > 0:
            pygame.draw.rect(self.screen, speed_col,
                             (px + 10, bar_y2, sp_fill, 6), border_radius=3)

        y_off += 30

        # ── Key-bindings ──────────────────────────────────────────────────────
        pygame.draw.line(self.screen, (*UI_BORDER, 80),
                         (px + 8, y_off), (px + panel_w - 8, y_off), 1)
        y_off += 5
        hints = [
            "[N]/[E]/[S]/[W] Set GREEN",
            "[R] Auto cycle   [A] Ambulance",
            "[P] Pause / Resume",
            "[+] Speed up   [-] Slow down",
            "[ESC] Quit",
        ]
        for hint in hints:
            h_surf = self.font_sm.render(hint, True, (105, 115, 135))
            self.screen.blit(h_surf, (px + 10, y_off))
            y_off += 15

    def _draw_pause_overlay(self):
        """Translucent black overlay with centred PAUSED text."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 115))
        self.screen.blit(overlay, (0, 0))

        text     = self.font_xl.render("|| PAUSED", True, (255, 255, 255))
        sub_text = self.font_med.render("Press  P  to resume", True, (180, 185, 195))
        cx, cy   = SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2

        t_rect  = text.get_rect(center=(cx, cy - 20))
        st_rect = sub_text.get_rect(center=(cx, cy + 28))
        self.screen.blit(text,     t_rect)
        self.screen.blit(sub_text, st_rect)
