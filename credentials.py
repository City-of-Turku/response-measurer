import keyring
import getpass

from utils import load_settings


def store_credentials(service_name: str, username: str) -> None:
    password = getpass.getpass(f"Enter password for {username}: ")
    keyring.set_password(service_name, username, password)
    print("Credentials stored successfully.")


def main() -> None:
    settings = load_settings('settings.json')
    username = settings.get('username')

    if not username:
        print('Username not defined in settings. Define username first and try again.')
        input('Press any key to exit.')
        return

    service_name = 'response-measurer'
    store_credentials(service_name, username)
    input('Press any key to exit.')


if __name__ == "__main__":
    main()