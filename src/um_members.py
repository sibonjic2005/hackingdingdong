from Main.traveller_input import create_traveller_from_input

def main_menu():
    while True:
        print("\n--- Urban Mobility Backend ---")
        print("1. Register new traveller")
        print("2. Exit")

        choice = input("Choose an option: ")

        if choice == "1":
            create_traveller_from_input()
        elif choice == "2":
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main_menu()
