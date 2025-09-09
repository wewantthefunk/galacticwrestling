from utils import *
from constants import *
from user_interactions import *

import json

def main():
    create_folder(WRESTLER_FOLDER)
    c = ''
    while c != EXIT_KEY and c != '1':
        clear_console()
        print("Welcome to the Galactic Wrestling Federation!")
        print("Choose:")
        print("1 - Wrestle!")
        print(EXIT_KEY + " - Quit")
        c = get_input()
        if c == EXIT_KEY:
            print("Goodbye!")
        elif c == "1":
            print("Time to Wrestle!")

    if c == EXIT_KEY:
        exit(0)

    choose_wrestler()

def choose_wrestler():
    clear_console()
    print("Choose your wrestler")

    print("1 - New Wrestler")

    files = get_files(WRESTLER_FOLDER)

    count = 2
    for file in files:
        wrestler = json.loads(read_file(WRESTLER_FOLDER + file))
        print(str(count) + " - " + wrestler['name'])
        count = count + 1

    print(EXIT_KEY + " - Exit")

    w = get_input()

    if w == '1':
        clear_console()
        print("Name your wrestler")
        wn = get_raw_input()
        build_wrestler(wn)


def build_wrestler(name):
    data = {
        "name": name
    }

    write_file(WRESTLER_FOLDER + name.lower() + USER_WRESTLER_EXTENSION, json.dumps(data, indent=4))

if __name__ == "__main__":
    main()