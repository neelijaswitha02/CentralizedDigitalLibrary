
import sqlite3

DATABASE = "library.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


def create_table():
    connection = get_connection()

    connection.execute("""
        CREATE TABLE IF NOT EXISTS books (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            author TEXT NOT NULL,
            category TEXT NOT NULL,
            isbn TEXT,
            status TEXT NOT NULL DEFAULT 'Available'
        )
    """)

    columns = connection.execute(
        "PRAGMA table_info(books)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

   
    if "isbn" not in column_names:
        connection.execute("ALTER TABLE books ADD COLUMN isbn TEXT")

    if "status" not in column_names:
         connection.execute(
            "ALTER TABLE books ADD COLUMN status TEXT NOT NULL DEFAULT 'Available'"
        )


    connection.commit()
    connection.close()



def get_all_books():
    connection = get_connection()

    books = connection.execute(
        "SELECT * FROM books ORDER BY id"
    ).fetchall()

    connection.close()
    return books



def add_book(title, author, category, isbn="", status="Available"):
    connection = get_connection()

    connection.execute(
        """
        INSERT INTO books (title, author, category, isbn, status)
        VALUES (?, ?, ?, ?, ?)
        """,
        (title, author, category, isbn, status)
    )

    connection.commit()
    connection.close()



def delete_book(book_id):
    connection = get_connection()

    connection.execute(
        "DELETE FROM books WHERE id = ?",
        (book_id,)
    )

    connection.commit()
    connection.close()



def update_book(
    book_id, title, author, category, isbn="", status="Available"
):
    connection = get_connection()

    connection.execute(
        """
        UPDATE books
        SET title = ?, author = ?, category = ?, isbn = ?, status = ?
        WHERE id = ?
        """,
        (title, author, category, isbn, status, book_id)
    )

    connection.commit()
    connection.close()


