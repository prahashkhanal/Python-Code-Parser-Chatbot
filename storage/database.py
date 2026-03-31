import sqlite3

DB_NAME = "project_knowledge.db"


def create_tables():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_path TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS functions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_id INTEGER,
            name TEXT,
            calls TEXT,
            FOREIGN KEY(file_id) REFERENCES files(id)
        )
    """)

    conn.commit()
    conn.close()


def insert_file(file_path):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO files (file_path) VALUES (?)",
        (file_path,)
    )

    file_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return file_id


def insert_function(file_id, name, calls):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO functions (file_id, name, calls) VALUES (?, ?, ?)",
        (file_id, name, str(calls))
    )

    conn.commit()
    conn.close()