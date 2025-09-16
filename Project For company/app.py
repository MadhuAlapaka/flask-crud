# app.py
import sqlite3
from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)
app.secret_key = "dev-secret"  # replace with .env in production
DB = "database.db"

def get_db_connection():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
    CREATE TABLE IF NOT EXISTS notes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    )""")
    conn.commit()
    conn.close()

init_db()

@app.route("/")
def index():
    conn = get_db_connection()
    notes = conn.execute("SELECT * FROM notes ORDER BY id DESC").fetchall()
    conn.close()
    return render_template("index.html", notes=notes)

@app.route("/create", methods=("GET", "POST"))
def create():
    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        if not title or not content:
            flash("Title and content are required.")
            return redirect(url_for("create"))
        conn = get_db_connection()
        conn.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))
    return render_template("create.html")

@app.route("/<int:id>/edit", methods=("GET", "POST"))
def edit(id):
    conn = get_db_connection()
    note = conn.execute("SELECT * FROM notes WHERE id = ?", (id,)).fetchone()
    conn.close()
    if not note:
        flash("Note not found.")
        return redirect(url_for("index"))

    if request.method == "POST":
        title = request.form["title"].strip()
        content = request.form["content"].strip()
        if not title or not content:
            flash("Title and content are required.")
            return redirect(url_for("edit", id=id))
        conn = get_db_connection()
        conn.execute("UPDATE notes SET title = ?, content = ? WHERE id = ?", (title, content, id))
        conn.commit()
        conn.close()
        return redirect(url_for("index"))

    return render_template("edit.html", note=note)

@app.route("/<int:id>/delete", methods=("POST",))
def delete(id):
    conn = get_db_connection()
    conn.execute("DELETE FROM notes WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    flash("Deleted.")
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(debug=True)
