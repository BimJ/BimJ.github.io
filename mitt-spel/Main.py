# main.py (excerpt)

import pyxel  # Pyxel game engine
import math   # Math module
import random # Random number module
import sprite # Import the sprite module

# ----Game settings---

W, H = 160, 120  # Game screen width and height
character_speed = 2  # Character movement speed
character_size = 8  # Character size
character_color = 11  # Character color (cyan)
gravity = 0.5  # Gravity affecting the character
jump_strength = -6  # Jump strength of the character
Player_spd = 1.4  # Player speed

#Enemy settings
Enemy_spd = 1.0  # Enemy movement speed



# Game
class Game:
    def __init__(self):
        #Initialize score
        self.score = 0

        self.is_on_ground = False  # Flag to check if the player is on the ground

        self.Game_sate = "START"  # Game state (can be "Start", "game_over", etc.)
        
        # Generate the level with platforms, coins, and enemies
        self.generate_level()
        
        # Create a player sprite at the bottom of the screen
        self.Player = sprite.PlayerSprite(10, H - 10 - character_size)
   
        # Initialize the window
        pyxel.init(W, H, title="Cave Traps 0.1")
        pyxel.load("cave_traps.pyxres")  # Load resources (images, sounds, etc.)
        # Start the game loop
        pyxel.run(self.update, self.draw)

    def generate_level(self):
        self.Platforms = []  # List to hold platform data
        self.Coins = []  # List to hold coin data
        self.Enemies = []  # List to hold enemy data

        # Starting position for player
        start_x = 0
        start_y = H - 10 #starting near the bottom of the screen
        start_width = 48
        start_height = 10

        self.Platforms.append((start_x, start_y, start_width, start_height))
        # Randomly generate platforms, coins, and enemies
        current_x = start_width + 16 # 16 pixels gap after the starting platform

        # Generate platforms until the end of the screen width
        while current_x < W * 20:  # Generate platforms for a level that is 20 screens wide
            width_in_blocks = random.randint(1, 4)  # Random width of 1 to 4 blocks (8 pixels each)
            Platform_width = width_in_blocks * 8  # Calculate platform width in pixels
            Platform_y = random.randint(50, 90)  # Random Y position for the platform

            # Add the platform
            self.Platforms.append((current_x, Platform_y, Platform_width, 8))

            # Randomly decide to add a coin above the platform with a 50% chance
            if random.random() < 0.5:
                Coin_x = current_x + Platform_width // 2 - 4  # Center the coin on the platform
                self.Coins.append({
                    "x": Coin_x, # Coin X position
                    "y": Platform_y - 12, # Position the coin above the platform
                    "Value": 10, # Coin value
                    "Collected": False
                }) # Add coin data to the list

            # Randomly decide gap between platforms
            gap = random.randint(1, 2) * 8  # Random gap of 1 to 3 blocks (8 pixels each)
            current_x += Platform_width + gap  # Move to the next platform position

    def check_coin_collection(self):
        """ Check if the player collects any coins """
        for Coin in self.Coins:
            if not Coin["Collected"]:  # Only check uncollected coins
                # Check for collision between player and coin
                if (self.Player.x < Coin["x"] + 8 and
                    self.Player.x + self.Player.w > Coin["x"] and
                    self.Player.y < Coin["y"] + 8 and
                    self.Player.y + self.Player.h > Coin["y"]):

                    Coin["Collected"] = True  # Mark the coin as collected
                    self.score += Coin["Value"]  # Increase score by coin value


    def control_Player(self):
        """ Control the player character based on input """  
        # 1. Stanna karaktären i sidled om ingen knapp trycks ner
        self.Player.vx = 0

        # 2. Lyssna efter höger och vänster
        if pyxel.btn(pyxel.KEY_LEFT):
            self.Player.vx = -character_speed  # Minus betyder vänster
        elif pyxel.btn(pyxel.KEY_RIGHT):
            self.Player.vx = character_speed   # Plus betyder höger
        # 3. Lyssna efter hopp (använd btnp så att man måste trycka på nytt för varje hopp)
        if pyxel.btnp(pyxel.KEY_UP) and self.is_on_ground:  # Check if the player is on the ground before allowing a jump
            self.Player.vy = jump_strength     # Din variabel från inställningarna
            
    def update(self):
        """ Update logic """
        # Check for game state and start the game when space is pressed
        if self.Game_sate == "START":
            if pyxel.btnp(pyxel.KEY_SPACE):  # Start the game when space is pressed
                self.Game_sate = "PLAYING"
            return  # Exit the update function to avoid further processing until the next frame

        # GAME OVER state handling can be added here if needed
        if self.Game_sate == "GAME_OVER":
            if pyxel.btnp(pyxel.KEY_SPACE):  # Restart the game when space is pressed
                self.Score = 0  # Reset score
                self.generate_level()  # Regenerate the level
                self.Player.x = 10  # Reset player position
                self.Player.y = H - 30  # Reset player position
                self.Player.vx = 0  # Reset player velocity
                self.Game_sate = "PLAYING"  # Change game state to playing
            return  # Exit the update function to avoid further processing until the next frame

        # Reads the player's input and updates the player's velocity accordingly
        self.control_Player() 

        # Apply gravity to the player's vertical velocity
        self.Player.vy += gravity 

        # Saves the position of the player before moving, to check for collisions later
        old_y = self.Player.y

        # Move the player based on its velocity and update its position
        self.Player.update()

        # Screen teleportation logic: If the player moves beyond the left or right edge of the screen, teleport them to the opposite side
        if self.Player.x > W: # If the player moves beyond the right edge of the screen
            self.Player.x = 0 # Teleport the player to the left edge of the screen
        elif self.Player.x + self.Player.w < 0: # If the player moves beyond the left edge of the screen
            self.Player.x = W - self.Player.w # Teleport the player to the right edge of the screen

        # If the player falls below the bottom of the screen and dies, reset the game state to "GAME_OVER"
        if self.Player.y > H:  # If the player falls below the bottom of the screen
            self.Game_sate = "GAME_OVER"  # Change game state to "GAME_OVER"

        # Check for collisions after moving the player and adjust position if necessary
        self.check_collision(old_y)
        self.check_coin_collection()  # Check if the player collects any coins  
        
    def draw(self):
        """ Drawing logic """
        pyxel.cls(6)  # Clear the screen with color 6 (light blue)

        # Platforms
        for px, py, pw, ph in self.Platforms:
            # Vi loopar igenom plattformens bredd och sätter en mark-bild var åttonde pixel
            for i in range(0, pw, 8):
                # Draw the platform image at the current position
                pyxel.blt(px + i, py, 0, 16, 8, 8, 8, 0)   

        # Coins
        for Coin in self.Coins:
            if not Coin["Collected"]:  # Only draw the coin if it hasn't been collected
                pyxel.blt(Coin["x"], Coin["y"], 0, 32, 0, 8, 8, 0)  # Draw the coin image

        # Draw the player sprite     
        self.Player.draw()

        #score counter
        pyxel.text(5, 5, "Score:{:04d}".format(self.score), 7)
        # Display score at (5, 5) with color 7 (white)

        # Game state messages (START, GAME OVER, etc.)
        if self.Game_sate == "START":
            pyxel.text(36, 46, "Press SPACE to Start", 0) #shadow
            pyxel.text(35, 45, "Press SPACE to Start", 7) #White text
        elif self.Game_sate == "GAME_OVER":
            pyxel.text(62, 41, "GAME OVER", 0)
            pyxel.text(61, 40, "GAME OVER", 8)  # Röd/rosa text för game over (färg 8)
            pyxel.text(40, 56, "PRESS SPACE TO RESTART", 0)
            pyxel.text(39, 55, "PRESS SPACE TO RESTART", 7)

    def check_collision(self, old_y):
     self.is_on_ground = False # Flag to check if the player is on the ground

     for px, py, pw, ph in self.Platforms:
            # Check if the player is falling and collides with a platform
            if (self.Player.x < px + pw and
                self.Player.x + self.Player.w > px and
                self.Player.y < py + ph and 
                self.Player.y + self.Player.h > py):

                # If collision detected, reset the player position to the top of the platform
                if self.Player.vy > 0 and old_y + self.Player.h <= py:
                    self.Player.y = py - self.Player.h  # Place player on top of the platform
                    self.Player.vy = 0  # Stop vertical movement (no longer falling)
                    self.is_on_ground = True

                elif self.Player.vy < 0 and old_y >= py + ph:
                    self.Player.y = py + ph  # Place player below the platform
                    self.Player.vy = 0  # Stop vertical movement (no longer moving up)
                # Add collision handling for horizontal movement if needed (e.g., hitting the sides of platforms)
                elif self.Player.vx > 0 and old_y + self.Player.h > py and old_y < py + ph:
                    self.Player.x = px - self.Player.w  # Place player to the left of the platform
                elif self.Player.vx < 0 and old_y + self.Player.h > py and old_y < py + ph:
                    self.Player.x = px + pw  # Place player to the right of the platform
def main():
    """ Main entry point """
    Game()

if __name__ == "__main__":
    main()