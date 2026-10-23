import sqlite3

DATABASE = "library.db"


def get_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def create_table():
    connection = get_connection()

    # Existing books table
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

    # Add missing columns to an existing database
    columns = connection.execute(
        "PRAGMA table_info(books)"
    ).fetchall()

    column_names = [column["name"] for column in columns]

    if "isbn" not in column_names:
        connection.execute(
            "ALTER TABLE books ADD COLUMN isbn TEXT"
        )

    if "status" not in column_names:
        connection.execute("""
            ALTER TABLE books
            ADD COLUMN status TEXT NOT NULL DEFAULT 'Available'
        """)

    # New table for student borrowing details
    connection.execute("""
        CREATE TABLE IF NOT EXISTS borrowings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            book_id INTEGER NOT NULL,
            student_name TEXT NOT NULL,
            roll_number TEXT NOT NULL,
            borrowed_on TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
            returned_on TEXT,
            FOREIGN KEY (book_id) REFERENCES books(id)
        )
    """)

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

    cursor = connection.execute("""
        INSERT INTO books (title, author, category, isbn, status)
        VALUES (?, ?, ?, ?, ?)
    """, (title, author, category, isbn, status))

    book_id = cursor.lastrowid

    connection.commit()
    connection.close()
    return book_id


def delete_book(book_id):
    connection = get_connection()

    # Remove borrowing records before deleting the book
    connection.execute(
        "DELETE FROM borrowings WHERE book_id = ?",
        (book_id,)
    )

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

    connection.execute("""
        UPDATE books
        SET title = ?, author = ?, category = ?, isbn = ?, status = ?
        WHERE id = ?
    """, (title, author, category, isbn, status, book_id))

    connection.commit()
    connection.close()


def add_borrowing(book_id, student_name, roll_number):
    connection = get_connection()

    connection.execute("""
        INSERT INTO borrowings (book_id, student_name, roll_number)
        VALUES (?, ?, ?)
    """, (book_id, student_name, roll_number))

    connection.commit()
    connection.close()


def get_active_borrowing(book_id):
    connection = get_connection()

    borrowing = connection.execute("""
        SELECT *
        FROM borrowings
        WHERE book_id = ? AND returned_on IS NULL
        ORDER BY id DESC
        LIMIT 1
    """, (book_id,)).fetchone()

    connection.close()
    return borrowing


def get_all_borrowings():
    connection = get_connection()

    borrowings = connection.execute("""
        SELECT
            borrowings.id,
            borrowings.book_id,
            borrowings.student_name,
            borrowings.roll_number,
            borrowings.borrowed_on,
            borrowings.returned_on,
            books.title AS book_title,
            books.author AS book_author
        FROM borrowings
        JOIN books ON books.id = borrowings.book_id
        ORDER BY borrowings.id DESC
    """).fetchall()

    connection.close()
    return borrowings


def mark_borrowing_returned(book_id):
    connection = get_connection()

    connection.execute("""
        UPDATE borrowings
        SET returned_on = CURRENT_TIMESTAMP
        WHERE book_id = ? AND returned_on IS NULL
    """, (book_id,))

    connection.commit()
    connection.close()

