import json
from getpass import getpass
from os import path, mkdir
from art import tprint
from script import start_check
from simple_term_menu import TerminalMenu


def check_scrapper_data(username):
    return path.exists(f"userdata/{username}_auth.json")


def user_init() -> str:
    return input("Hello, please enter username: ")


def create_user_datafile(auth_file_path):
    print("Let's save your Microsoft account")
    email = input("Enter your email: ")

    # Use getpass to hide password input on the terminal
    password = getpass("Enter your password: ")

    auth_data = {"email": email, "password": password}

    with open(auth_file_path, "w+") as file:
        json.dump(auth_data, file, indent=2)


def get_user_data(auth_file_path):
    with open(auth_file_path, 'r') as file:
        data = json.load(file)
    return data


def app_process():
    print("\033c", end="")
    banner_text = "XboxCheck"
    tprint(banner_text)

    userdata_dir = "userdata"
    if not path.exists(userdata_dir):
        mkdir(userdata_dir)

    username = user_init()
    auth_file_path = path.join(userdata_dir, f"{username}_auth.json")

    if not check_scrapper_data(username):
        create_user_datafile(auth_file_path)

    menu = TerminalMenu([
        "Check Token",
        "Print my data",
        "Change the data",
        "Change user",
        "Exit"
    ])
    return_menu = TerminalMenu(['Return'])

    print("\033c", end="")

    while True:
        data = get_user_data(auth_file_path)

        tprint(banner_text)
        menu.show()

        match menu.chosen_menu_index:
            case 0:
                token = input("Enter token: ")
                email = data.get('email', None)
                password = data.get('password', None)

                start_check(token=token,
                            email=email,
                            password=password)

                return_menu.show()
            case 1:
                print(f"Email: {data.get('email', None)}")
                print(f"Password {data.get('password', None)}")
                return_menu.show()
            case 2:
                create_user_datafile(auth_file_path)
                return_menu.show()
            case 3:
                print("\033c", end="")
                return False
            case 4:
                print("\033c", end="")
                tprint("Bye")
                return True

        print("\033c", end="")


def main():
    while True:
        if app_process():
            break


if __name__ == "__main__":
    main()
