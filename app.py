from flask import Flask, render_template, request, redirect, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
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
          posts.likes,
          users.username
       FROM posts
       JOIN users ON posts.user_id = users.id
       ORDER BY posts.created_at DESC
    """)

    posts = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("index.html", posts=posts)


# 🔹 LOGIN
@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cur.fetchone()

    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect("/")

    return redirect("/?error=login")


# 🔹 REGISTER (з авто-логіном)
@app.route("/register", methods=["POST"])
def register():

    username = request.form["username"]
    email = request.form["email"]
    password = request.form["password"]

    hashed = generate_password_hash(password)

    try:
        conn = get_db_connection()
        cur = conn.cursor()

        cur.execute(
            "INSERT INTO users (username, email, password) VALUES (%s,%s,%s)",
            (username, email, hashed)
        )

        conn.commit()

        user_id = cur.lastrowid
        conn.close()

        # 🔥 авто-логін
        session["user_id"] = user_id
        session["username"] = username

        return redirect("/")

    except mysql.connector.errors.IntegrityError:
        return redirect("/?error=email")


@app.route("/logout")
def logout():
    session.clear()
    return redirect("/")


@app.route("/user/<username>")
def profile(username):

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # користувач
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()

    # пости користувача
    cur.execute("""
        SELECT * FROM posts
        WHERE user_id = %s
        ORDER BY created_at DESC
    """, (user["id"],))

    posts = cur.fetchall()

    conn.close()

    return render_template("profile.html", user=user, posts=posts)

@app.route("/like/<int:post_id>")
def like(post_id):

    if "user_id" not in session:
        return redirect("/")

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("UPDATE posts SET likes = likes + 1 WHERE id = %s", (post_id,))
    conn.commit()
    conn.close()

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)