from database import create_tables
from menu import menu


def main():
    create_tables()
    menu()


if __name__ == "__main__":
    main()