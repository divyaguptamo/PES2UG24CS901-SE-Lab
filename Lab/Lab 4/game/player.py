import pygame


class Puller:
    """Represents a puller character anchor on either side of the rope."""

    MAX_LEAN_PIXELS = 22

    def __init__(self, x, y, color, label, back_dir=-1):
        self.x = x
        self.y = y
        self.color = color
        self.label = label
        self.back_dir = back_dir  # -1 = leans left when pulling, +1 = leans right
        self.lean = 0.0           # current smoothed lean, -1..1 (positive = backward)
        self.font = pygame.font.SysFont(None, 24)

    def update(self, target_lean):
        """Ease the lean toward the target so movement looks smooth."""
        self.lean += (target_lean - self.lean) * 0.15

    def render(self, surface):
        """Draw avatar (leaning) and label."""
        dx = int(self.lean * self.back_dir * self.MAX_LEAN_PIXELS)

        # Body: bottom stays planted, top shifts to create the lean
        body_points = [
            (self.x - 20, self.y + 35),
            (self.x + 20, self.y + 35),
            (self.x + 20 + dx, self.y - 35),
            (self.x - 20 + dx, self.y - 35),
        ]
        pygame.draw.polygon(surface, self.color, body_points)

        # Head moves a bit further than the body top
        head_x = self.x + int(dx * 1.3)
        pygame.draw.circle(surface, (240, 210, 180), (head_x, self.y - 50), 16)

        # Name / control tag
        label_surf = self.font.render(self.label, True, (240, 240, 240))
        surface.blit(label_surf, (self.x - label_surf.get_width() // 2, self.y + 45))