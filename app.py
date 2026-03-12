from flask import Flask, render_template, request, redirect, session, url_for
import mysql.connector
from config import MYSQL_HOST, MYSQL_USER, MYSQL_PASSWORD, MYSQL_DB, MYSQL_PORT, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

def get_db_connection():
   return mysql.connector.connect(
   host=MYSQL_HOST,
   user=MYSQL_USER,
   password=MYSQL_PASSWORD,
   database=MYSQL_DB,
   port=MYSQL_PORT
)

@app.route("/")
def home():

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT
            posts.id,
            posts.title,
            posts.content,
            posts.created_at,
            users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
    """)

    posts = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", posts=posts)

@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "INSERT INTO users (username, email, password) VALUES (%s,%s,%s)",
        (username, email, password)
    )

    conn.commit()

    cursor.execute(
        "SELECT * FROM users WHERE email = %s",
        (email,)
    )

    user = cursor.fetchone()

    session["user_id"] = user["id"]
    session["username"] = user["username"]

    cursor.close()
    conn.close()

    return redirect("/")

@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute(
        "SELECT * FROM users WHERE email=%s AND password=%s",
        (email, password)
    )

    user = cursor.fetchone()

    cursor.close()
    conn.close()

    if user:
        session["user_id"] = user["id"]
        session["username"] = user["username"]

    return redirect("/")

@app.route("/logout")
def logout():

    session.clear()

    return redirect("/")

@app.route("/create_post", methods=["GET","POST"])
def create_post():

    if "user_id" not in session:
        return redirect("/")

    return render_template("create_post.html")


if __name__ == "__main__":
    app.run(debug=True)