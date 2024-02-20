from js import document

def view_all_contacts():
    if len(contacts) == 0:
        print("Your contacts are empty!")
        return

    # Show this first
    # for name in contacts:
    #    print(f"{name}'s phone number: {contacts[name]}")

    # Refactor to this
    for name, number in contacts.items():
        js.document.innetHTML(f"{name}'s phone number: {number}")


# HW 1
def view_contact():
    name = input("What is the name of the contact? ")
    if name not in contacts:
        print(f"{name} is not in your contacts!")
        return

    print(f"{name}'s number is {contacts[name]}")


def add_contact():
    name = input("Enter contact name: ")
    number = input("Enter contact number: ")
    if name in contacts:
        print(f"{name} is already in your contacts!")
        return

    contacts[name] = number
    print(f"Added {name} to your contacts")


# HW 1
def update_contact():
    name = input("Enter contact name: ")
    number = input("Enter contact number: ")
    if name not in contacts:
        print(f"{name} is not in your contacts!")
        return

    contacts[name] = number


# HW 1
def remove_contact():
    name = input("Enter contact name: ")
    if name not in contacts:
        print(f"{name} is not in your contacts!")
        return

    contacts.pop(name)
    print(f"Removed {name} from your contacts.")


options = """\
    (1) View All Contacts (2) View Contact (3) Add Contact
    (4) Update Contact (5) Remove Contact (6) Exit
"""


contacts = {
    "Steve": "823-111-2384",
    "Kim": "823-843-2435",
}


def input(s):
    return js.window.prompt(s)
    


choice = int(input("Enter a number"))

if choice == 1:
    body = document.getElementById("body")
    body.innerHTML = "Hello"

# while True:
#     choice = input("Hello")
#     if choice == 1:
#         view_all_contacts()
#         break
#     elif choice == 2:
#         view_contact()
#     elif choice == 3:
#         add_contact()
#     elif choice == 4:
#         update_contact()
#     elif choice == 5:
#         remove_contact()
#     elif choice == 6:
#         break
#     else:
#         print(f"{choice} is not a valid option")
