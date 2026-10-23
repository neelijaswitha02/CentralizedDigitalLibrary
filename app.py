from flask import Flask, render_template, request, redirect, url_for, flash
import database

app = Flask(__name__)
app.secret_key = "change-this-to-a-random-secret"

# Create database tables
database.create_table()

# Add sample books only when the database is empty
if not database.get_all_books():
    database.add_book("Python Programming", "John Smith", "Technology")
    database.add_book("Introduction to Science", "Mary Johnson", "Science")
    database.add_book("The Great Adventure", "David Brown", "Fiction")
    database.add_book("Learning Mathematics", "Robert Wilson", "Education")


@app.route("/")
def home():
    query = request.args.get("q", "").strip().casefold()
    category = request.args.get("category", "").strip()
    sort_by = request.args.get("sort", "title").strip()

    books = database.get_all_books()

    if sort_by not in {"title", "author"}:
        sort_by = "title"

    filtered_books = [
        book for book in books
        if (
            not query
            or query in book["title"].casefold()
            or query in book["author"].casefold()
        )
        and (
            not category
            or book["category"] == category
        )
    ]

    filtered_books.sort(key=lambda book: book[sort_by].casefold())

    return render_template(
        "index.html",
        books=filtered_books,
        sort_by=sort_by
    )


@app.route("/book/<int:book_id>")
def book_detail(book_id):
    books = database.get_all_books()

    book = next(
        (item for item in books if item["id"] == book_id),
        None
    )

    if book is None:
        return "Book not found", 404

    borrowing = database.get_active_borrowing(book_id)

    return render_template(
        "book_detail.html",
        book=book,
        borrowing=borrowing
    )


@app.route("/borrow/<int:book_id>", methods=["POST"])
def borrow_book(book_id):
    books = database.get_all_books()

    book = next(
        (item for item in books if item["id"] == book_id),
        None
    )

    if book is None:
        return "Book not found", 404

    if book["status"] != "Available":
        flash("This book is already borrowed.")
        return redirect(url_for("book_detail", book_id=book_id))

    student_name = request.form.get("student_name", "").strip()
    roll_number = request.form.get("roll_number", "").strip()

    if not student_name or not roll_number:
        flash("Please enter the student's name and roll number.")
        return redirect(url_for("book_detail", book_id=book_id))

    # Save student borrowing details
    database.add_borrowing(book_id, student_name, roll_number)

    # Update the book status
    database.update_book(
        book_id,
        book["title"],
        book["author"],
        book["category"],
        book["isbn"] or "",
        "Borrowed"
    )

    flash("Book borrowed successfully!")
    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/return/<int:book_id>", methods=["POST"])
def return_book(book_id):
    books = database.get_all_books()

    book = next(
        (item for item in books if item["id"] == book_id),
        None
    )

    if book is None:
        return "Book not found", 404

    if book["status"] == "Borrowed":
        # Record the return date
        database.mark_borrowing_returned(book_id)

        # Make the book available again
        database.update_book(
            book_id,
            book["title"],
            book["author"],
            book["category"],
            book["isbn"] or "",
            "Available"
        )

        flash("Book returned successfully!")

    return redirect(url_for("book_detail", book_id=book_id))


@app.route("/borrowings")
def borrowing_records():
    borrowings = database.get_all_borrowings()

    return render_template(
        "borrowing_records.html",
        borrowings=borrowings
    )


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        isbn = request.form.get("isbn", "").strip()

        allowed_categories = {
            "Technology", "Science", "Fiction", "Education"
        }

        if title and author and category in allowed_categories:
            database.add_book(title, author, category, isbn)
            flash("Book added successfully!")
        else:
            flash("Please enter a valid title, author, and category.")

        return redirect(url_for("admin"))

    books = database.get_all_books()

    stats = {
        "total": len(books),
        "Technology": sum(
            1 for book in books if book["category"] == "Technology"
        ),
        "Science": sum(
            1 for book in books if book["category"] == "Science"
        ),
        "Fiction": sum(
            1 for book in books if book["category"] == "Fiction"
        ),
        "Education": sum(
            1 for book in books if book["category"] == "Education"
        ),
    }

    return render_template(
        "admin.html",
        books=books,
        stats=stats
    )


@app.route("/admin/edit/<int:book_id>", methods=["GET", "POST"])
def edit_book(book_id):
    books = database.get_all_books()

    book = next(
        (item for item in books if item["id"] == book_id),
        None
    )

    if book is None:
        return "Book not found", 404

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        isbn = request.form.get("isbn", "").strip()
        status = request.form.get("status", "Available").strip()

        allowed_categories = {
            "Technology", "Science", "Fiction", "Education"
        }

        if status not in {"Available", "Borrowed"}:
            status = "Available"

        if title and author and category in allowed_categories:
            database.update_book(
                book_id, title, author, category, isbn, status
            )
            flash("Book updated successfully!")
            return redirect(url_for("admin"))

        flash("Please enter valid book details.")

    return render_template("edit_book.html", book=book)


@app.route("/admin/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    database.delete_book(book_id)
    flash("Book deleted successfully!")
    return redirect(url_for("admin"))


if __name__ == "__main__":
    app.run(debug=True)

