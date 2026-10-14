
from flask import Flask, render_template, request, redirect, url_for, flash
import database

app = Flask(__name__)

app.secret_key = "change-this-to-a-random-secret"


# Create the database table
database.create_table()

# Add sample books only when the database is empty
if not database.get_all_books():
    database.add_book(
        "Python Programming", "John Smith", "Technology"
    )
    database.add_book(
        "Introduction to Science", "Mary Johnson", "Science"
    )
    database.add_book(
        "The Great Adventure", "David Brown", "Fiction"
    )
    database.add_book(
        "Learning Mathematics", "Robert Wilson", "Education"
    )
    


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

    return render_template(
        "book_detail.html",
        book=book
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


@app.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        status = request.form.get("status", "Available").strip()
        if status not in {"Available", "Borrowed"}:
            status = "Available"

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        isbn = request.form.get("isbn", "").strip()

        allowed_categories = {
            "Technology", "Science", "Fiction", "Education"
        }

        if title and author and category in allowed_categories:
            database.add_book(title, author, category, isbn, status)
            flash("Book added successfully!")


        return redirect(url_for("admin"))

    books = database.get_all_books()

    stats = {
        "total": len(books),
        "Technology": sum(1 for book in books if book["category"] == "Technology"),
        "Science": sum(1 for book in books if book["category"] == "Science"),
        "Fiction": sum(1 for book in books if book["category"] == "Fiction"),
        "Education": sum(1 for book in books if book["category"] == "Education"),
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
        status = request.form.get("status", "Available").strip()
        if status not in {"Available", "Borrowed"}:
            status = "Available"

        title = request.form.get("title", "").strip()
        author = request.form.get("author", "").strip()
        category = request.form.get("category", "").strip()
        isbn = request.form.get("isbn", "").strip()

        allowed_categories = {
            "Technology", "Science", "Fiction", "Education"
        }

        if title and author and category in allowed_categories:
            database.update_book(
                book_id, title, author, category, isbn, status
            )
            flash("Book updated successfully!")
            return redirect(url_for("admin"))

    return render_template("edit_book.html", book=book)



@app.route("/admin/delete/<int:book_id>", methods=["POST"])
def delete_book(book_id):
    database.delete_book(book_id)
    flash("Book deleted successfully!")
    return redirect(url_for("admin"))



if __name__ == "__main__":
    app.run(debug=True)
