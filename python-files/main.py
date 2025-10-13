def add_item(inventory):
    """Adds a new item and its quantity to the inventory."""
    name = input("Enter item name: ").strip().title()
    while True:
        try:
            quantity = int(input(f"Enter quantity for {name}: "))
            if quantity < 0:
                print("Quantity cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a whole number for quantity.")

    # Update or add the item
    inventory[name] = inventory.get(name, 0) + quantity
    print(f"\n✅ Added {quantity} of {name}. New stock: {inventory[name]}")

def view_inventory(inventory):
    """Displays all items and their quantities."""
    if not inventory:
        print("\nInventory is currently empty.")
        return

    print("\n--- Current Inventory ---")
    # Sort the inventory alphabetically by item name
    sorted_items = sorted(inventory.items())
    for item, quantity in sorted_items:
        print(f"| {item:<20} | Quantity: {quantity}")
    print("-------------------------")

def remove_item(inventory):
    """Removes a specified quantity of an existing item."""
    if not inventory:
        print("\nInventory is empty. Nothing to remove.")
        return

    name = input("Enter the name of the item to remove stock from: ").strip().title()
    if name not in inventory:
        print(f"\nItem '{name}' not found in inventory.")
        return

    while True:
        try:
            qty_to_remove = int(input(f"Enter quantity of {name} to remove (current stock: {inventory[name]}): "))
            if qty_to_remove < 0:
                print("Quantity to remove cannot be negative.")
                continue
            break
        except ValueError:
            print("Invalid input. Please enter a whole number.")

    if qty_to_remove > inventory[name]:
        print(f"\n⚠️ Warning: Can only remove {inventory[name]} units. Removing all stock.")
        inventory[name] = 0
    else:
        inventory[name] -= qty_to_remove
        print(f"\n✅ Removed {qty_to_remove} of {name}.")

    if inventory[name] == 0:
        # Optionally remove the item entirely if stock hits zero
        del inventory[name]
        print(f"Item {name} stock reached zero and was removed from the list.")
    else:
        print(f"Remaining stock for {name}: {inventory[name]}")

def main():
    """Main function to run the inventory system loop."""
    inventory = {} # Initialize the main inventory dictionary
    print("Welcome to the Simple Inventory System!")

    while True:
        print("\n--- Menu ---")
        print("1. Add/Receive Stock")
        print("2. View Inventory")
        print("3. Remove/Ship Stock")
        print("4. Exit")
        choice = input("Enter your choice (1-4): ").strip()

        if choice == '1':
            add_item(inventory)
        elif choice == '2':
            view_inventory(inventory)
        elif choice == '3':
            remove_item(inventory)
        elif choice == '4':
            print("Exiting system. Goodbye! 👋")
            break
        else:
            print("\nInvalid choice. Please select a number from 1 to 4.")

if __name__ == "__main__":
    main()