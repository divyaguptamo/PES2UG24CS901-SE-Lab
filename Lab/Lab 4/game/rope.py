import math
import pygame


class Rope:
    def __init__(self, screen_width, screen_height):
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.center_y = screen_height // 2
        self.marker_x = screen_width // 2

        self.left_win_x = 180
        self.right_win_x = screen_width - 180
        self.pull_step = 12

    def pull_left(self, strength=1.0):
        self.marker_x -= int(self.pull_step * strength)

    def pull_right(self, strength=1.0):
        self.marker_x += int(self.pull_step * strength)

    def check_winner(self):
        if self.marker_x <= self.left_win_x:
            return "PLAYER"
        if self.marker_x >= self.right_win_x:
            return "COMPUTER"
        return None

    def reset(self):
        self.marker_x = float(self.screen_width // 2)
        self.velocity = 0.0

    def tension(self):
        """0.0 = flag at center (slack rope), 1.0 = flag at a goal line (taut)."""
        half = self.screen_width // 2
        span = half - self.left_win_x
        return min(1.0, abs(self.marker_x - half) / span)

    def rope_y(self, x):
        """Vertical position of the rope at screen x: sag when slack, vibrate when taut."""
        left, right = 60, self.screen_width - 60
        t = (x - left) / (right - left)
        t = max(0.0, min(1.0, t))
        envelope = 4 * t * (1 - t)  # 0 at the ends, 1 in the middle

        tension = self.tension()
        sag = (1 - tension) * 10 * envelope
        vibration = tension * 5 * envelope * math.sin(x * 0.08 + pygame.time.get_ticks() * 0.04)
        return self.center_y + sag + vibration

    def render(self, surface):
        # Rope as a wavy polyline
        points = [
            (x, self.rope_y(x))
            for x in range(60, self.screen_width - 60 + 1, 8)
        ]
        pygame.draw.lines(surface, (180, 140, 90), False, points, 10)

        pygame.draw.line(
            surface,
            (50, 200, 50),
            (self.left_win_x, self.center_y - 40),
            (self.left_win_x, self.center_y + 40),
            4
        )
        pygame.draw.line(
            surface,
            (200, 50, 50),
            (self.right_win_x, self.center_y - 40),
            (self.right_win_x, self.center_y + 40),
            4
        )

        pygame.draw.line(
            surface,
            (120, 120, 120),
            (self.screen_width // 2, self.center_y - 20),
            (self.screen_width // 2, self.center_y + 20),
            2
        )

        # Flag rides on the rope
        flag_y = int(self.rope_y(self.marker_x))
        flag_rect = pygame.Rect(int(self.marker_x) - 12, flag_y - 24, 24, 48)
        pygame.draw.rect(surface, (230, 40, 40), flag_rect, border_radius=4)
        pygame.draw.rect(surface, (255, 255, 255), flag_rect, width=2, border_radius=4)