# Coffie shop, where you can buy coffee with gold coins. The coffee shop has a menu with different types of coffee, each with a price in gold coins. The user can select the type of coffee they want to buy and the number of cups they want to purchase. The program will then calculate the total cost and check if the user has enough gold coins to make the purchase. If the user has enough coins, the program will deduct the cost from their total and confirm the purchase. If not, it will inform the user that they do not have enough coins. The  player can do shores to earn more gold coins. Plpayer can aske to check their current gold coin balance at any time. The program will continue to run until the user decides to exit the coffee shop.

#Basic variables
goldcoins = 20  # Starting gold coins for the user
energy = 50  # Starting energy for the user
if energy <= 0:
    print("You are too tired to continue.You crashed and lost all your gold coins. Game over.")
    exit()
if energy > 100:
    print("You are too energetic and ran into a wall. You lost 5 gold coins.)")
    goldcoins -= 5
Chores = ["Wash dishes", "Clean tables", "Restock supplies", "Take out trash"]
b = "Select a chore to do: "
for chore in Chores:
    b += chore + ", "
choices = ["Check menu", "Buy coffee", "Do chores", "Check balance", "Exit"]
a = "Select your option: "
for choice in choices:
    a += choice + ", "

#coffie choices, price and the amount of energy it adds to the user
coffee_menu = {
    "Espresso": {"price": 5, "energy": 15},
    "Latte": {"price": 7, "energy": 10},
    "Cappuccino": {"price": 6, "energy": 12},
    "Mocha": {"price": 8, "energy": 18},
    "Americano": {"price": 4, "energy": 8}
}



print("Welcome to the Coffee Shop!")
print("You have", goldcoins, "gold coins and", energy, "energy.")
print("would you like to check the menu or do chores to earn more gold coins?")
choice_input = input(a)
if choice_input == "Check menu":
    print("Here is the coffee menu:")
    for coffee, details in coffee_menu.items():
        print(f"{coffee}: {details['price']} gold coins, adds {details['energy']} energy")
elif choice_input == "Do chores":
    print("You decided to do chores and earn more gold coins!")
    chore_input = input(b)
    if chore_input in Chores:
        print(f"You did the chore: {chore_input} and earned gold coins!")
        goldcoins += 5
        energy -= 10
elif choice_input == "Check balance":
    print("You have", goldcoins, "gold coins and", energy, "energy.")
    choice_input = input(a)
elif choice_input == "Exit":
    print("Thank you for visiting the Coffee Shop!")
    exit()
else:
    print("Invalid choice. Please try again.")
    choice_input = input(a)
