import random
import pygame
from game.rope import Rope
from game.player import Puller

# --- Task 2: panic surge settings ---
BASE_COOLDOWN = 180        # ms between computer pulls (normal)
PANIC_COOLDOWN = 90        # ms between computer pulls (panic)
PANIC_STRENGTH = 1.3       # extra pull strength during panic
PANIC_RATIO = 0.30         # panic when flag is 30% of the way to the player's goal

# --- Task 4: match timer settings ---
SUDDEN_DEATH_TIME = 45     # seconds
SUDDEN_DEATH_MULT = 2.0    # pull distance multiplier in sudden death


class GameEngine:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.rope = Rope(width, height)
        self.player = Puller(90, height // 2, (50, 120, 220), "PLAYER (A/D)", back_dir=-1)
        self.computer = Puller(width - 90, height // 2, (220, 80, 50), "COMPUTER", back_dir=1)

        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"

        self.computer_pull_cooldown = BASE_COOLDOWN
        self.last_computer_pull = pygame.time.get_ticks()

        # Panic threshold: flag position at which the computer starts surging
        half = width // 2
        self.panic_x = half - PANIC_RATIO * (half - self.rope.left_win_x)
        self.panic = False

        # Timer / sudden death
        self.match_start = pygame.time.get_ticks()
        self.elapsed = 0.0
        self.sudden_death = False

        self.font_big = pygame.font.SysFont(None, 48)
        self.font_small = pygame.font.SysFont(None, 26)

    def pull_multiplier(self):
        return SUDDEN_DEATH_MULT if self.sudden_death else 1.0

    def handle_event(self, event):
        if self.game_state != "PLAYING":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset()
            return

        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_a, pygame.K_d):
                # Only pull when the player alternates keys
                if event.key != self.last_key:
                    self.rope.pull_left(1.0 * self.pull_multiplier())
                    self.last_key = event.key

    def update_lean(self):
        # Positive = player has momentum (flag left of center)
        half = self.width // 2
        span = half - self.rope.left_win_x
        momentum = (half - self.rope.marker_x) / span
        momentum = max(-1.0, min(1.0, momentum))
        self.player.update(momentum)
        self.computer.update(-momentum)

    def update(self):
        self.update_lean()

        if self.game_state != "PLAYING":
            return

        now = pygame.time.get_ticks()

        # Task 4: timer and sudden death
        self.elapsed = (now - self.match_start) / 1000.0
        self.sudden_death = self.elapsed >= SUDDEN_DEATH_TIME

        # Task 2: panic surge
        self.panic = self.rope.marker_x <= self.panic_x
        self.computer_pull_cooldown = PANIC_COOLDOWN if self.panic else BASE_COOLDOWN

        if now - self.last_computer_pull >= self.computer_pull_cooldown:
            strength = random.uniform(0.7, 1.2)
            if self.panic:
                strength *= PANIC_STRENGTH
            strength *= self.pull_multiplier()
            self.rope.pull_right(strength)
            self.last_computer_pull = now

        result = self.rope.check_winner()
        if result:
            self.winner = result
            self.game_state = "GAME_OVER"

    def reset(self):
        self.rope.reset()
        self.player.lean = 0.0
        self.computer.lean = 0.0
        self.last_key = None
        self.winner = None
        self.game_state = "PLAYING"
        self.panic = False
        self.sudden_death = False
        self.elapsed = 0.0
        self.match_start = pygame.time.get_ticks()
        self.computer_pull_cooldown = BASE_COOLDOWN
        self.last_computer_pull = pygame.time.get_ticks()

    def render(self, screen):
        screen.fill((30, 32, 36))

        mud_rect = pygame.Rect(self.width // 2 - 120, self.height // 2 - 80, 240, 160)
        pygame.draw.rect(screen, (45, 38, 30), mud_rect, border_radius=12)

        self.rope.render(screen)
        self.player.render(screen)
        self.computer.render(screen)

        # Timer at top of screen
        timer_color = (255, 80, 80) if self.sudden_death else (240, 240, 240)
        timer_surf = self.font_small.render(
            f"Time: {int(self.elapsed)}s", True, timer_color
        )
        screen.blit(timer_surf, (self.width // 2 - timer_surf.get_width() // 2, 12))

        inst_surf = self.font_small.render(
            "Alternate [A] and [D] keys rapidly to pull!", True, (210, 210, 210)
        )
        screen.blit(inst_surf, (self.width // 2 - inst_surf.get_width() // 2, 40))

        # Status labels
        if self.sudden_death:
            sd_surf = self.font_big.render("SUDDEN DEATH!", True, (255, 60, 60))
            screen.blit(sd_surf, (self.width // 2 - sd_surf.get_width() // 2, 68))
        elif self.panic and self.game_state == "PLAYING":
            p_surf = self.font_small.render("COMPUTER PANIC SURGE!", True, (255, 170, 40))
            screen.blit(p_surf, (self.width // 2 - p_surf.get_width() // 2, 68))

        if self.game_state == "GAME_OVER":
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))

            win_text = f"{self.winner} WINS!"
            color = (80, 220, 80) if self.winner == "PLAYER" else (240, 80, 80)
            text_surf = self.font_big.render(win_text, True, color)
            screen.blit(
                text_surf,
                (self.width // 2 - text_surf.get_width() // 2, self.height // 2 - 50)
            )

            restart_surf = self.font_small.render(
                "Press [R] to Play Again", True, (240, 240, 240)
            )
            screen.blit(
                restart_surf,
                (self.width // 2 - restart_surf.get_width() // 2, self.height // 2 + 10)
            )