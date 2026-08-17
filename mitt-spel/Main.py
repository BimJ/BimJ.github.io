# Main.py
# Main game file.
# Handles the player, platform generation, coin collection, door unlock, and win/lose states.

import pyxel
import random
import sprite

W, H = 160, 120
LEVEL_WIDTH = 480  # the level is 3x wider than the screen, camera scrolls to follow the player

CHARACTER_SPEED = 2.0
GRAVITY = 0.25
JUMP_STRENGTH = -3.7
PLAYER_SIZE = 8

def clamp(value, low, high):
    return max(low, min(value, high))

class Game:
    def __init__(self):
        self.score = 0
        self.coins_collected = 0
        self.game_state = "START"

        self.is_on_ground = False
        self.camera_x = 0  # how far the camera has scrolled

        self.door_active = False
        self.door_x = 0
        self.door_y = 0

        self.generate_level()
        self.Player = sprite.PlayerSprite(10, H - 20)

        pyxel.init(W, H, title="Cave Traps 0.1")
        pyxel.load("cave_traps.pyxres")
        pyxel.run(self.update, self.draw)

    def reset_game(self):
        self.score = 0
        self.coins_collected = 0
        self.game_state = "PLAYING"
        self.is_on_ground = False
        self.door_active = False
        self.door_x = 0
        self.door_y = 0
        self.camera_x = 0

        self.generate_level()
        self.Player.x = 10
        self.Player.y = H - 20
        self.Player.vx = 0
        self.Player.vy = 0
        self.is_on_ground = False

    def simulate_jump_reach(self, rel_target_y):
        """
        Simulates a jump using the real game physics (JUMP_STRENGTH, GRAVITY, CHARACTER_SPEED)
        and returns how far horizontally the player would have traveled by the time
        they reach a given relative height (rel_target_y).

        rel_target_y is relative to the jump's starting height:
        - negative = target is HIGHER than the start (player needs to jump up to it)
        - positive = target is LOWER than the start (player is falling down to it)

        Returns None if the target is physically too high to ever reach (jump apex too low).
        """
        vy = JUMP_STRENGTH
        y = 0.0
        x = 0.0
        max_frames = 200  # safety limit so this can never loop forever

        for _ in range(max_frames):
            vy += GRAVITY
            y += vy
            x += CHARACTER_SPEED

            if rel_target_y <= 0:
                # Target is at or above start height, check if we've risen high enough
                if y <= rel_target_y:
                    return x
            else:
                # Target is below start height, check if we've fallen far enough
                if y >= rel_target_y:
                    return x

        return None  # never reached the target height, it's out of jump range

    def generate_level(self):
        # Creates platforms spread across a level wider than the screen,
        # so real gaps and varied heights are always possible.
        # Every platform is guaranteed reachable using real jump physics.
        self.Platforms = []
        self.Coins = []
        self.Enemies = []

        start_width = 40
        self.Platforms.append((0, H - 10, start_width, 10))

        platform_count = 6

        previous_y = H - 10
        current_x = start_width
        recent_heights = [previous_y]

        # Safety margin subtracted from the max possible jump distance,
        # so the player has a little room for error and isn't forced to
        # land on the exact last possible frame
        safety_margin = 8

        for i in range(platform_count):
            width = random.randint(20, 32)

            # Try to pick a height, then verify (and if needed, adjust) that
            # it's actually reachable given the real jump physics
            if random.random() < 0.3:
                candidate_y = previous_y + random.randint(-14, 14)
            else:
                candidate_y = random.randint(24, 92)
            candidate_y = clamp(candidate_y, 24, 92)

            if len(recent_heights) >= 2 and abs(candidate_y - recent_heights[-1]) < 6 and abs(candidate_y - recent_heights[-2]) < 6:
                candidate_y = clamp(candidate_y + random.choice([-20, 20]), 24, 92)

            # Relative height of the candidate platform compared to the previous one
            rel_target_y = candidate_y - previous_y

            # Ask the physics simulation how far the player can actually jump to reach this height
            max_reach = self.simulate_jump_reach(rel_target_y)

            if max_reach is None:
                # Too high to reach at all, pull the height down closer to previous_y
                candidate_y = previous_y - 18  # a safe, reachable rise
                candidate_y = clamp(candidate_y, 24, 92)
                rel_target_y = candidate_y - previous_y
                max_reach = self.simulate_jump_reach(rel_target_y)
                if max_reach is None:
                    max_reach = 30  # ultimate fallback, should not normally trigger

            # The usable gap can never be larger than what physics allows
            max_gap = max(10, int(max_reach) - safety_margin)

            # Pick the actual gap within the physically safe range
            min_gap = min(16, max_gap)  # keep a bit of breathing room, but never exceed max_gap
            gap = random.randint(min_gap, max_gap) if max_gap > min_gap else max_gap

            x = current_x + gap
            y = candidate_y

            self.Platforms.append((x, y, width, 8))
            recent_heights.append(y)

            previous_y = y
            current_x = x + width

        eligible_indexes = list(range(1, len(self.Platforms)))
        coin_indexes = random.sample(eligible_indexes, min(3, len(eligible_indexes)))

        for idx in coin_indexes:
            plat = self.Platforms[idx]
            coin_x = plat[0] + plat[2] // 2 - 4
            coin_y = clamp(plat[1] - 12, 12, 100)

            self.Coins.append({
                "x": coin_x,
                "y": coin_y,
                "Value": 10,
                "Collected": False
            })

        door_candidates = [i for i in eligible_indexes if i not in coin_indexes]
        if not door_candidates:
            door_candidates = eligible_indexes

        door_platform_index = random.choice(door_candidates)
        door_platform = self.Platforms[door_platform_index]
        self.door_x = door_platform[0] + door_platform[2] // 2 - 4
        self.door_y = door_platform[1] - 8

        hazard_candidates = [
            i for i in eligible_indexes
            if i not in coin_indexes and i != door_platform_index
        ]

        for idx in hazard_candidates:
            plat = self.Platforms[idx]
            if random.random() < 0.7 and plat[2] >= 20:
                hazard_type = random.choice(["enemy", "spike", "ball"])
                self.spawn_hazard(plat, hazard_type)

    def spawn_hazard(self, plat, hazard_type):
        px, py, pw, ph = plat

        if hazard_type == "spike":
            hazard = sprite.SpikeSprite(px + pw // 2 - 4, py - 8)
            hazard.min_x = px
            hazard.max_x = px + pw - 8
        elif hazard_type == "ball":
            # Ball bounces horizontally across the whole LEVEL,
            # and also bounces vertically between the ground and a max height
            hazard = sprite.BallSprite(px + 4, py - 16)
            hazard.min_x = 0
            hazard.max_x = LEVEL_WIDTH - 8
            hazard.vx = 1.2

            # Vertical bounce range: bounces between the platform's height
            # and a fixed height above it
            hazard.vy = -2.0  # initial upward velocity for the bounce
            hazard.ground_y = py - 8   # the "floor" the ball bounces off of
            hazard.min_y = py - 40     # how high the ball can bounce
        else:
            hazard = sprite.EnemySprite(px + 4, py - 8)
            hazard.min_x = px
            hazard.max_x = px + pw - 8
            hazard.vx = 0.6

        hazard.hazard_type = hazard_type
        self.Enemies.append(hazard)

    def update_enemies(self):
        for enemy in self.Enemies:
            if enemy.hazard_type == "spike":
                continue

            elif enemy.hazard_type == "ball":
                # Horizontal wall bounce (left/right across the level)
                enemy.x += enemy.vx
                if enemy.x <= enemy.min_x:
                    enemy.x = enemy.min_x
                    enemy.vx = abs(enemy.vx)
                elif enemy.x >= enemy.max_x:
                    enemy.x = enemy.max_x
                    enemy.vx = -abs(enemy.vx)

                # Vertical bounce (up/down like a real bouncing ball)
                enemy.vy += GRAVITY * 0.6  # slightly lighter gravity for a bouncier feel
                enemy.y += enemy.vy

                if enemy.y >= enemy.ground_y:
                    enemy.y = enemy.ground_y
                    enemy.vy = -abs(enemy.vy) * 0.95  # bounce back up, losing a little energy

                    # Keep a minimum bounce strength so it never fully stops bouncing
                    if abs(enemy.vy) < 1.8:
                        enemy.vy = -2.2

                elif enemy.y <= enemy.min_y:
                    enemy.y = enemy.min_y
                    enemy.vy = abs(enemy.vy)  # bounce back down

            else:
                # Enemy patrols only within its own platform
                enemy.x += enemy.vx
                if enemy.x <= enemy.min_x:
                    enemy.x = enemy.min_x
                    enemy.vx = abs(enemy.vx)
                elif enemy.x >= enemy.max_x:
                    enemy.x = enemy.max_x
                    enemy.vx = -abs(enemy.vx)

    def check_enemy_collision(self):
        for enemy in self.Enemies:
            if (
                self.Player.x < enemy.x + enemy.w and
                self.Player.x + self.Player.w > enemy.x and
                self.Player.y < enemy.y + enemy.h and
                self.Player.y + self.Player.h > enemy.y
            ):
                self.game_state = "GAME_OVER"
                return

    def check_coin_collection(self):
        for coin in self.Coins:
            if not coin["Collected"]:
                if (
                    self.Player.x < coin["x"] + 8 and
                    self.Player.x + self.Player.w > coin["x"] and
                    self.Player.y < coin["y"] + 8 and
                    self.Player.y + self.Player.h > coin["y"]
                ):
                    coin["Collected"] = True
                    self.score += coin["Value"]
                    self.coins_collected += 1

                    if self.coins_collected >= 3 and not self.door_active:
                        self.door_active = True

    def control_Player(self):
        self.Player.vx = 0

        if pyxel.btn(pyxel.KEY_LEFT):
            self.Player.vx = -CHARACTER_SPEED
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.Player.vx = CHARACTER_SPEED

        if pyxel.btnp(pyxel.KEY_UP) and self.is_on_ground:
            self.Player.vy = JUMP_STRENGTH
            self.is_on_ground = False

        if not pyxel.btn(pyxel.KEY_UP) and self.Player.vy < 0:
            self.Player.vy += 0.15

    def check_collision(self, old_y):
        self.is_on_ground = False

        for px, py, pw, ph in self.Platforms:
            if (
                self.Player.x < px + pw and
                self.Player.x + self.Player.w > px and
                self.Player.y < py + ph and
                self.Player.y + self.Player.h > py
            ):
                if self.Player.vy > 0 and old_y + self.Player.h <= py:
                    self.Player.y = py - self.Player.h
                    self.Player.vy = 0
                    self.is_on_ground = True
                elif self.Player.vy < 0 and old_y >= py + ph:
                    self.Player.y = py + ph
                    self.Player.vy = 0
                elif self.Player.vx > 0 and old_y + self.Player.h > py and old_y < py + ph:
                    self.Player.x = px - self.Player.w
                elif self.Player.vx < 0 and old_y + self.Player.h > py and old_y < py + ph:
                    self.Player.x = px + pw

    def update(self):
        if self.game_state == "START":
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.game_state = "PLAYING"
            return

        if self.game_state == "GAME_OVER":
            if pyxel.btnp(pyxel.KEY_SPACE):
                self.reset_game()
            return

        self.control_Player()
        self.Player.vy += GRAVITY
        old_y = self.Player.y
        self.Player.update()

        # Keep the player inside the level bounds (no wrap-around anymore)
        self.Player.x = clamp(self.Player.x, 0, LEVEL_WIDTH - self.Player.w)

        if self.Player.y > H + 20:
            self.game_state = "GAME_OVER"

        self.check_collision(old_y)
        self.check_coin_collection()
        self.update_enemies()
        self.check_enemy_collision()

        # Camera follows the player, keeping them roughly centered,
        # but never scrolls past the level edges
        target_camera_x = self.Player.x - W // 2
        self.camera_x = clamp(target_camera_x, 0, LEVEL_WIDTH - W)

        if self.door_active:
            if (
                self.Player.x < self.door_x + 8 and
                self.Player.x + self.Player.w > self.door_x and
                self.Player.y < self.door_y + 8 and
                self.Player.y + self.Player.h > self.door_y
            ):
                self.next_level()

    def draw(self):
        pyxel.cls(6)
        cam = self.camera_x

        # Draw platforms, offset by the camera position
        for px, py, pw, ph in self.Platforms:
            for i in range(0, pw, 8):
                pyxel.blt(px + i - cam, py, 0, 16, 8, 8, 8, 0)

        # Draw coins, offset by the camera
        for coin in self.Coins:
            if not coin["Collected"]:
                pyxel.blt(coin["x"] - cam, coin["y"], 0, 32, 0, 8, 8, 0)

        # Draw hazards, offset by the camera
        for enemy in self.Enemies:
            pyxel.blt(enemy.x - cam, enemy.y, 0, self._hazard_uv(enemy.hazard_type)[0], self._hazard_uv(enemy.hazard_type)[1], enemy.w, enemy.h, 0)

        # Draw door, offset by the camera
        if self.door_active:
            pyxel.blt(self.door_x - cam, self.door_y, 0, 32, 8, 8, 8, 0)

        # Draw player, offset by the camera
        pyxel.blt(self.Player.x - cam, self.Player.y, 0, 0, 0, self.Player.w, self.Player.h, 0)

        pyxel.text(5, 5, f"Score:{self.score:04d}", 7)
        pyxel.text(5, 13, f"Coins: {self.coins_collected}/3", 10)

        if self.game_state == "START":
            pyxel.text(W // 2 - 40, H // 2 - 4, "Press SPACE to Start", 0)
            pyxel.text(W // 2 - 41, H // 2 - 5, "Press SPACE to Start", 7)

        elif self.game_state == "GAME_OVER":
            pyxel.text(W // 2 - 30, H // 2 - 18, "YOU LOSE!", 0)
            pyxel.text(W // 2 - 31, H // 2 - 19, "YOU LOSE!", 8)
            pyxel.text(W // 2 - 52, H // 2 + 6, "Press SPACE to restart", 0)
            pyxel.text(W // 2 - 53, H // 2 + 5, "Press SPACE to restart", 7)

    def _hazard_uv(self, hazard_type):
        # Returns the (u, v) tile coordinates for a given hazard type.
        # Update these to match cave_traps.pyxres if your tiles are elsewhere.
        if hazard_type == "enemy":
            return (8, 0)
        elif hazard_type == "spike":
            return (16, 0)
        else:
            return (24, 0)

    def next_level(self):
        self.coins_collected = 0
        self.door_active = False
        self.door_x = 0
        self.door_y = 0
        self.camera_x = 0

        self.generate_level()
        self.Player.x = 10
        self.Player.y = H - 20
        self.Player.vx = 0
        self.Player.vy = 0
        self.is_on_ground = False

def main():
    Game()

if __name__ == "__main__":
    main()