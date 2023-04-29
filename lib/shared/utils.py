import sqlite3


class SQLite:

    def __init__(self, file="") -> None:
        print("DATABASE FILE: ", file)
        self.file = file

    def __enter__(self):
        self.conn = sqlite3.connect(self.file)
        return self.conn, self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.close()


def generate_response(response: str = "", action: str = "", next: str = "") -> dict:
    result = {
        "response": response,
        "action": action,
        "next": next
    }
    return result
