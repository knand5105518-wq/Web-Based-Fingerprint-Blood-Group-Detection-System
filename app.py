from flask import Flask, render_template, request, redirect, session
import os
import sqlite3
from model.predict import predict_blood_group

app = Flask(__name__)
app.secret_key = 'hakuna_secret_key'

# ------------------- Upload Folder -------------------
UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

if not os.path.isdir(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ------------------- Database -------------------
def init_db():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        password TEXT
    )
    ''')

    cur.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT,
        image TEXT,
        result TEXT
    )
    ''')

    conn.commit()
    conn.close()

init_db()

# ------------------- Routes -------------------

# Home
@app.route('/')
def index():
    return render_template('index.html')


# Register
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (user, pwd))

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')


# Login (Clear previous session)
@app.route('/login', methods=['GET', 'POST'])
def login():
    session.clear()

    if request.method == 'POST':
        user = request.form['username']
        pwd = request.form['password']

        conn = sqlite3.connect('database.db')
        cur = conn.cursor()

        cur.execute("SELECT * FROM users WHERE username=? AND password=?", (user, pwd))
        data = cur.fetchone()

        conn.close()

        if data:
            session['user'] = user
            return redirect('/upload')
        else:
            return "Invalid Login!"

    return render_template('login.html')


# Upload (Protected)
@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'user' not in session:
        return redirect('/login')

    if request.method == 'POST':

        # 🔥 Check file मौजूद है या नहीं
        if 'fingerprint' not in request.files:
            return "No file part"

        file = request.files['fingerprint']

        # 🔥 Empty filename check
        if file.filename == "":
            return "Please upload an image"

        if file:
            filename = file.filename.replace(" ", "_")
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)

            file.save(filepath)

            # 🔥 Prediction
            result = predict_blood_group(filepath)

            # 🔥 Save to DB
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()

            cur.execute(
                "INSERT INTO predictions (username, image, result) VALUES (?, ?, ?)",
                (session['user'], filename, result)
            )

            conn.commit()
            conn.close()

            return render_template('result.html', result=result, image=filepath)

    return render_template('upload.html')


# History Page
@app.route('/history')
def history():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("SELECT image, result FROM predictions WHERE username=?", (session['user'],))
    data = cur.fetchall()

    conn.close()

    return render_template('history.html', data=data)


# Clear History
@app.route('/clear_history')
def clear_history():
    if 'user' not in session:
        return redirect('/login')

    conn = sqlite3.connect('database.db')
    cur = conn.cursor()

    cur.execute("DELETE FROM predictions WHERE username=?", (session['user'],))

    conn.commit()
    conn.close()

    return redirect('/history')


# Logout
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect('/login')


# Run App
if __name__ == '__main__':
    app.run(debug=True)