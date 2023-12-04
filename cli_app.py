import json
import sys
from getpass import getpass
from os import path, mkdir
from art import tprint
from script import start_single_check, start_pool_check
from simple_term_menu import TerminalMenu
from userdata_handler import create_user_datafile, get_user_data, check_scrapper_data


def user_init() -> str:
    return input("Hello, please enter username: ")


def create_user(auth_file_path):
    print("Let's save your Microsoft account")
    email = input("Enter your email: ")

    # Use getpass to hide password input on the terminal
    password = getpass("Enter your password: ")
    create_user_datafile(auth_file_path, email, password)


def app_process():
    print("\033c", end="")
    banner_text = "XboxCheck"
    tprint(banner_text)
    username = user_init()

    userdata_dir = "userdata"
    if not path.exists(userdata_dir):
        mkdir(userdata_dir)
    auth_file_path = path.join(userdata_dir, f"{username}_auth.json")

    if not check_scrapper_data(username):
        create_user(auth_file_path)

    menu = TerminalMenu([
        "Check Single Token",
        "Check Multiple Tokens",
        "Print my data",
        "Change the data",
        "Change user",
        "Exit"
    ])
    return_menu = TerminalMenu(['Return'])

    print("\033c", end="")

    while True:

        tprint(banner_text)
        menu.show()

        auth_data = get_user_data(auth_file_path)

        match menu.chosen_menu_index:
            case 0:
                token = input("Enter token: ")
                start_single_check(token=token,
                                   data=auth_data)
                return_menu.show()
            case 1:
                data_path = input("Enter path to .xlsx file: ")
                filename = input("Enter a file name to save the processed tokens: ")
                try:
                    start_pool_check(data_path, auth_data, filename)
                except Exception as e:
                    print(f"Sorry, {e}")
                    return_menu.show()
                    continue
                print(f"The check is completed, the results are recorded in the [processed] folder"
                      f" in the {filename}.xlsx file")
                return_menu.show()
            case 2:
                print(f"Email: {auth_data.get('email', None)}")
                print(f"Password {auth_data.get('password', None)}")
                return_menu.show()
            case 3:

                create_user(auth_file_path)
                return_menu.show()
            case 4:
                print("\033c", end="")
                return
            case 5:
                print("\033c", end="")
                tprint("Bye")
                sys.exit(0)

        print("\033c", end="")


def main():
    while True:
        app_process()


if __name__ == "__main__":
    main()
