import pyxel
import math
import random

class baseSprite:
    def __init__(self, x, y, width, height, color):
        # Constructor to initialize the sprite's position, size, and color
        self.x = x  # X coordinate
        self.y = y  # Y coordinate
        self.w = width  # Image width
        self.h = height  # Image height
        self.color = color  # Color of the sprite
        self.vx = 0  # Velocity in the X direction
        self.vy = 0  # Velocity in the Y direction



    # Update Logic
    def update(self):
        self.x += self.vx  # Move in the X direction
        self.y += self.vy  # Move in the Y direction

    # Draw Logic
    def draw(self):
        pass

    # Movement Logic
    def move(self, spd, deg):
        rad = deg * (math.pi / 180)  # Convert degrees to radians
        self.vx = spd * math.cos(rad)  # Calculate velocity in X direction
        self.vy = spd * math.sin(rad)  # Calculate velocity in Y direction

    def flip_x(self):
        self.vx *= -1  # Reverse the X velocity to flip the sprite horizontally

class PlayerSprite(baseSprite):
    def __init__(self, x, y):
        # Initialize the character sprite with specific size and color
        super().__init__(x, y, 8, 8, 11)  # width, height, color

    def draw(self):
        # Draw the character sprite at its current position
        pyxel.blt(self.x, self.y, 0, 0, 0, self.w, self.h, 0)  # Draw from image bank 0, source (0, 0), size (w, h), transparent color 0

class EnemySprite(baseSprite):
    def __init__(self, x, y):
        # Initialize the enemy sprite with specific size and color
        super().__init__(x, y, 8, 8, 8)  # width, height, color

    def draw(self):
        # Draw the enemy sprite at its current position
        pyxel.blt(self.x, self.y, 0, 8, 0, self.w, self.h, 0)  # Draw from image bank 0, source (8, 0), size (w, h), transparent color 0