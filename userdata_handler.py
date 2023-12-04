import json
from os import path


def get_user_data(auth_file_path):
    with open(auth_file_path, 'r') as file:
        data = json.load(file)
    return data


def create_user_datafile(auth_file_path, email, password):
    auth_data = {"email": email, "password": password}

    with open(auth_file_path, "w+") as file:
        json.dump(auth_data, file, indent=2)


def check_scrapper_data(username):
    return path.exists(f"userdata/{username}_auth.json")
