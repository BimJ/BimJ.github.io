# main.py (excerpt)

import pyxel  # Pyxel game engine
import math   # Math module
import random # Random number module

# ----Game settings---

W, H = 160, 120  # Game screen width and height
character_speed = 2  # Character movement speed
character_size = 8  # Character size
character_color = 11  # Character color (cyan)
gravity = 0.5  # Gravity affecting the character
jump_strength = -8  # Jump strength of the character

# Game
class Game:
    def __init__(self):
        #Initialize score
        self.score = 0
        
        """ Constructor """ # 1. Initialize the window
        pyxel.init(W, H, title="Cave Traps 0.1")
        pyxel.load("cave_traps.pyxres")  # Load resources (images, sounds, etc.)

        # 2. player settings (position, velocity, etc.)
        

        # 3. Start the game loop
        pyxel.run(self.update, self.draw)

    def update(self):
        """ Update logic """
        pass

    def draw(self):
        """ Drawing logic """
        pyxel.cls(6)  # Clear the screen with color 6 (light blue)

        #score counter
        pyxel.text(5, 5, "Score:{:04d}".format(self.score), 7)  # Display score at (5, 5) with color 7 (white)

        #character
        pyxel.blt(0, 112, 0, 0, 0, 8, 8, 0)  # character sprite at (0, 112) from image bank 0, source (0, 0), size (8, 8), transparent color 0

def main():
    """ Main entry point """
    Game()

if __name__ == "__main__":
    main()