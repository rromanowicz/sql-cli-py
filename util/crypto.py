import os.path

from cryptography.fernet import Fernet
from dotenv import load_dotenv

F_KEY: str = "F_KEY"


def encrypt(input: str) -> str:
    if input is not None and len(input) != 0 and input != "None":
        cipher = Fernet(os.getenv(F_KEY).encode())
        return cipher.encrypt(input.encode()).decode()
    return input


def decrypt(input: str) -> str:
    if input is not None and len(input) != 0 and input != "None":
        cipher = Fernet(os.getenv(F_KEY).encode())
        return cipher.decrypt(input.encode()).decode()
    return input


def load_env() -> None:
    if not os.path.isfile(".env"):
        with open(".env", "w") as file:
            file.write(f"{F_KEY}={Fernet.generate_key().decode()}")

    load_dotenv()
