

MENU = """
=== Inventory Manager ===
1. List all items
2. View item details
3. Add new item
4. Update item price/stock
5. Delete item
6. Find item on OpenFoodFacts
7. Quit
"""

ACTIONS = {
    "1": list_items,
    "2": view_item,
    "3": add_item,
    "4": update_item,
    "5": delete_item,
    "6": find_on_api,
}


def main():
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "7":
            print("Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print("Invalid option, please choose 1-7.")


if __name__ == "__main__":
    main()


MENU = """
=== Inventory Manager ===
1. List all items
2. View item details
3. Add new item
4. Update item price/stock
5. Delete item
6. Find item on OpenFoodFacts
7. Quit
"""

ACTIONS = {
    "1": list_items,
    "2": view_item,
    "3": add_item,
    "4": update_item,
    "5": delete_item,
    "6": find_on_api,
}


def main():
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "7":
            print("Goodbye!")
            break
        action = ACTIONS.get(choice)
        if action:
            action()
        else:
            print("Invalid option, please choose 1-7.")


if __name__ == "__main__":
    main()
