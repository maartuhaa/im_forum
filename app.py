from flask import Flask, render_template, request, redirect, session # Flask — фреймворк; render_template HTML; request дані з форми; redirect — перекидання; session — зберігає логін
import mysql.connector
from flask import jsonify # повертає дані у форматі JSON (для JS)
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

 # головна сторінка
@app.route("/")
def home():

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    user_id = session.get("user_id", 0)
# всі пости + лайки
    cur.execute("""  
        SELECT   
            posts.id,
            posts.title,
            posts.content,
            posts.created_at,
            users.username,

            COUNT(post_likes.id) as likes,

            MAX(CASE WHEN post_likes.user_id = %s THEN 1 ELSE 0 END) as liked

        FROM posts
        JOIN users ON posts.user_id = users.id
        LEFT JOIN post_likes ON posts.id = post_likes.post_id

        GROUP BY posts.id
        ORDER BY posts.created_at DESC
    """, (user_id,))

    posts = cur.fetchall()  # отримуємо всі пости
# останні 6 постів
    cur.execute("""
        SELECT
            posts.id,
            posts.title,
            posts.content,
            posts.created_at,
            users.username
        FROM posts
        JOIN users ON posts.user_id = users.id
        ORDER BY posts.created_at DESC
        LIMIT 6
    """)

    latest_posts = cur.fetchall()

    cur.execute("""
        SELECT
            comments.post_id,
            comments.content,
            users.username,
            comments.created_at
        FROM comments
        JOIN users ON comments.user_id = users.id
        ORDER BY comments.created_at ASC
    """)

    comments = cur.fetchall()

    conn.close()
 # передаємо все в HTML
    return render_template( 
        "index.html",
        posts=posts,
        comments=comments,
        latest_posts=latest_posts  
    )


@app.route("/login", methods=["POST"])
def login():

    email = request.form["email"]
    password = request.form["password"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM users WHERE email = %s", (email,)) # шукаємо юзера по email
    user = cur.fetchone() # беремо одного користувача

    conn.close()

    if user and check_password_hash(user["password"], password):
        session["user_id"] = user["id"]
        session["username"] = user["username"]
        return redirect("/") # перекидаємо на головну

    return redirect("/?error=login")


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
        return jsonify({"error": "unauthorized"}), 401

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    # чи вже є лайк
    cur.execute(
        "SELECT id FROM post_likes WHERE user_id = %s AND post_id = %s",
        (session["user_id"], post_id)
    )
    existing = cur.fetchone()

    if existing:
        cur.execute(
            "DELETE FROM post_likes WHERE user_id = %s AND post_id = %s",  # анлайк
            (session["user_id"], post_id)
        )
        liked = False
    else:
        cur.execute(
            "INSERT INTO post_likes (user_id, post_id) VALUES (%s, %s)",  # ставимо лайк
            (session["user_id"], post_id)
        )
        liked = True

    conn.commit() # зберігаємо зміни

    cur.execute(
        "SELECT COUNT(*) as count FROM post_likes WHERE post_id = %s",
        (post_id,)
    )
    count = cur.fetchone()["count"]

    conn.close()

    return jsonify({
        "liked": liked,
        "count": count
    })


@app.route("/comment/<int:post_id>", methods=["POST"])
def add_comment(post_id):

    if "user_id" not in session:  # перевірка логіну
        return jsonify({"error": "unauthorized"}), 401

    content = request.form["content"].strip()  # strip — прибирає пробіли
    parent_id = request.form.get("parent_id") 

    if not content or len(content) > 300:
        return jsonify({"error": "invalid"}), 400

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "INSERT INTO comments (content, user_id, post_id, parent_id) VALUES (%s, %s, %s, %s)", # додаємо коментар
        (content, session["user_id"], post_id, parent_id)
    )

    conn.commit()

    comment_id = cur.lastrowid

    cur.execute("""
        SELECT comments.id, comments.content, comments.parent_id, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.id = %s
    """, (comment_id,))

    new_comment = cur.fetchone()

    conn.close()

    return jsonify(new_comment)

@app.route("/comments/<int:post_id>") # отримати всі коментарі для поста (API)
def get_comments(post_id): 
    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT comments.id, comments.content, comments.parent_id, users.username
        FROM comments
        JOIN users ON comments.user_id = users.id
        WHERE comments.post_id = %s
        ORDER BY comments.created_at ASC
    """, (post_id,))

    comments = cur.fetchall()
    conn.close()

    return jsonify(comments)

@app.route("/like_comment/<int:comment_id>")
def like_comment(comment_id):

    if "user_id" not in session:
        return jsonify({"error": "unauthorized"}), 401

    user_id = session["user_id"]

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM comment_likes WHERE user_id = %s AND comment_id = %s",
        (user_id, comment_id)
    )
    existing = cur.fetchone()

    if existing:
        cur.execute(
            "DELETE FROM comment_likes WHERE user_id = %s AND comment_id = %s",
            (user_id, comment_id)
        )
        liked = False
    else:
        cur.execute(
            "INSERT INTO comment_likes (user_id, comment_id) VALUES (%s, %s)",
            (user_id, comment_id)
        )
        liked = True

    conn.commit()

    cur.execute(
        "SELECT COUNT(*) as count FROM comment_likes WHERE comment_id = %s",
        (comment_id,)
    )
    count = cur.fetchone()["count"]

    conn.close()

    return jsonify({
        "liked": liked,
        "count": count
    })

@app.route("/posts")
def posts_page():

    conn = get_db_connection()
    cur = conn.cursor(dictionary=True, buffered=True) 

    user_id = session.get("user_id", 0)

    cur.execute("""
        SELECT
            posts.id,
            posts.title,
            posts.content,
            posts.created_at,
            users.username,

            COUNT(post_likes.id) as likes,
            MAX(CASE WHEN post_likes.user_id = %s THEN 1 ELSE 0 END) as liked

        FROM posts
        JOIN users ON posts.user_id = users.id
        LEFT JOIN post_likes ON posts.id = post_likes.post_id

        GROUP BY posts.id
        ORDER BY posts.created_at DESC
    """, (user_id,))

    posts = cur.fetchall()

    for post in posts: # проходимо по кожному посту

        cur.execute("""
            SELECT comments.id, comments.content, users.username
            FROM comments
            JOIN users ON comments.user_id = users.id
            WHERE comments.post_id = %s
            ORDER BY comments.created_at ASC
        """, (post["id"],))

        all_comments = cur.fetchall()

        post["all_comments"] = all_comments
        post["preview_comments"] = all_comments[:2] # тільки перші 2 

    cur.close()
    conn.close()

    return render_template("posts.html", posts=posts)

if __name__ == "__main__":
    app.run(debug=True)  # запускає сервер (debug=True — показує помилки)