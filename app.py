from flask import Flask, render_template, request, redirect, session, url_for
import sqlite3

app = Flask(__name__)
app.secret_key = "contact_secret_key"

# ================= DATABASE =================

def get_db():
    conn = sqlite3.connect("contacts.db")
    conn.row_factory = sqlite3.Row
    return conn


# Create tables (runs once on startup)
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS admin (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT UNIQUE,
    password TEXT
)
""")

conn.execute("""
CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    phone TEXT,
    email TEXT,
    address TEXT
)
""")
conn.commit()
conn.close()


# ================= AUTH =================

@app.route("/")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        conn = get_db()
        user = conn.execute(
            "SELECT * FROM admin WHERE username=? AND password=?",
            (username, password)
        ).fetchone()
        conn.close()

        if user:
            session["admin"] = username
            return redirect(url_for("dashboard"))
        else:
            return "Invalid credentials"

    return redirect("/")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


# ================= DASHBOARD =================

@app.route("/home")
def dashboard():
    if "admin" not in session:
        return redirect("/")
    return render_template("index.html")


# ================= CONTACTS =================

@app.route("/add", methods=["GET", "POST"])
def add_contact():
    if "admin" not in session:
        return redirect("/")

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        conn = get_db()
        conn.execute(
            "INSERT INTO contacts (name, phone, email, address) VALUES (?, ?, ?, ?)",
            (name, phone, email, address)
        )
        conn.commit()
        conn.close()

        return redirect("/view")

    return render_template("add.html")


@app.route("/view")
def view_contacts():
    if "admin" not in session:
        return redirect("/")

    conn = get_db()
    contacts = conn.execute("SELECT * FROM contacts").fetchall()
    conn.close()

    return render_template("view.html", contacts=contacts)


@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit_contact(id):
    if "admin" not in session:
        return redirect("/")

    conn = get_db()

    if request.method == "POST":
        name = request.form["name"]
        phone = request.form["phone"]
        email = request.form["email"]
        address = request.form["address"]

        conn.execute("""
            UPDATE contacts
            SET name=?, phone=?, email=?, address=?
            WHERE id=?
        """, (name, phone, email, address, id))
        conn.commit()
        conn.close()

        return redirect("/view")

    contact = conn.execute(
        "SELECT * FROM contacts WHERE id=?", (id,)
    ).fetchone()
    conn.close()

    return render_template("edit.html", contact=contact)


@app.route("/delete/<int:id>")
def delete_contact(id):
    if "admin" not in session:
        return redirect("/")

    conn = get_db()
    conn.execute("DELETE FROM contacts WHERE id=?", (id,))
    conn.commit()
    conn.close()

    return redirect("/view")


# ================= RUN =================

if __name__ == "__main__":
    app.run(debug=False)