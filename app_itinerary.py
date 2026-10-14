from flask import Flask, render_template_string, request, redirect, url_for, session
import os
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "gwangju_secret_key_rienz27"  # Dibutuhkan untuk session login

DB_NAME = "database.db"

# Inisialisasi Database SQLite
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Tabel User
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    ''')
    # Tabel Itinerary terikat ke username
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS itineraries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT NOT NULL,
            day TEXT NOT NULL,
            time TEXT NOT NULL,
            place TEXT NOT NULL,
            category TEXT NOT NULL,
            desc TEXT NOT NULL,
            done INTEGER DEFAULT 0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Template HTML dengan Tampilan macOS/iOS + Halaman Login/Register
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="id">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Gwangju Trip Itinerary</title>
    <style>
        :root {
            --bg-color: #F5F5F7;
            --card-bg: #FFFFFF;
            --text-color: #1D1D1F;
            --text-muted: #86868B;
            --accent-color: #007AFF;
            --border-color: #E5E5EA;
            --danger-color: #FF3B30;
        }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "SF Pro Text", "Helvetica Neue", Arial, sans-serif;
            background-color: var(--bg-color);
            color: var(--text-color);
            margin: 0;
            padding: 24px;
            display: flex;
            justify-content: center;
        }
        .mac-window {
            width: 100%;
            max-width: 700px;
            background: var(--card-bg);
            border-radius: 14px;
            box-shadow: 0 20px 40px rgba(0, 0, 0, 0.08);
            border: 1px solid var(--border-color);
            overflow: hidden;
            margin-bottom: 40px;
        }
        .window-header {
            background: #EBEBEC;
            padding: 12px 16px;
            display: flex;
            align-items: center;
            border-bottom: 1px solid var(--border-color);
        }
        .window-dots {
            display: flex;
            gap: 8px;
        }
        .dot { width: 12px; height: 12px; border-radius: 50%; }
        .dot-close { background: #FF5F56; }
        .dot-min { background: #FFBD2E; }
        .dot-max { background: #27C93F; }
        .window-title {
            flex-grow: 1;
            text-align: center;
            font-size: 13px;
            font-weight: 600;
            color: #3A3A3C;
            margin-right: 52px;
        }
        .content-body { padding: 24px; }
        h2 { margin: 0 0 4px 0; font-size: 22px; font-weight: 700; letter-spacing: -0.5px; }
        .subtitle { color: var(--text-muted); font-size: 13px; margin-bottom: 20px; }
        
        /* Auth Container */
        .auth-container {
            max-width: 400px;
            margin: 40px auto;
            background: var(--card-bg);
            padding: 30px;
            border-radius: 14px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.06);
            border: 1px solid var(--border-color);
        }
        .auth-container h2 { text-align: center; margin-bottom: 20px; }
        
        input, select, textarea {
            width: 100%;
            padding: 10px 12px;
            border: 1px solid var(--border-color);
            border-radius: 8px;
            font-size: 13px;
            box-sizing: border-box;
            background: #FAFAFC;
            color: var(--text-color);
            margin-bottom: 12px;
        }
        button.btn-primary {
            background: var(--accent-color);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            width: 100%;
        }
        button.btn-primary:hover { opacity: 0.9; }
        
        .top-nav {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 12px;
            border-bottom: 1px solid var(--border-color);
        }
        .logout-link {
            color: var(--danger-color);
            text-decoration: none;
            font-size: 12px;
            font-weight: 600;
        }
        
        .add-form {
            background: #FAFAFC;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 24px;
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .card {
            background: #FAFAFC;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
            display: flex;
            align-items: flex-start;
            gap: 14px;
        }
        .card.done { opacity: 0.5; background: #F2F2F7; }
        .card.done .place-title { text-decoration: line-through; color: var(--text-muted); }
        input[type="checkbox"] { width: 20px; height: 20px; margin-top: 3px; accent-color: var(--accent-color); cursor: pointer; }
        .info { flex-grow: 1; }
        .day-tag { font-size: 11px; font-weight: 700; color: #FF9500; text-transform: uppercase; margin-bottom: 2px; }
        .place-title { font-size: 15px; font-weight: 600; margin: 2px 0 6px 0; }
        .badge { display: inline-block; background: #EBF5FF; color: var(--accent-color); font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 4px; margin-bottom: 6px; }
        .desc { font-size: 13px; color: #3A3A3C; line-height: 1.4; }
        .btn-delete { background: transparent; border: none; color: var(--danger-color); font-size: 16px; cursor: pointer; }
        .error-msg { color: var(--danger-color); font-size: 12px; margin-bottom: 10px; text-align: center; }
        .success-msg { color: #34C759; font-size: 12px; margin-bottom: 10px; text-align: center; }
    </style>
</head>
<body>

{% if not session.get('username') %}
    <!-- HALAMAN LOGIN / REGISTER -->
    <div class="auth-container">
        <h2>🇰🇷 Gwangju Trip</h2>
        <div class="subtitle" style="text-align:center; margin-bottom:16px;">Silakan login atau buat akun baru</div>
        
        {% if error %}
            <div class="error-msg">{{ error }}</div>
        {% endif %}
        {% if success %}
            <div class="success-msg">{{ success }}</div>
        {% endif %}

        <form action="/login" method="POST">
            <input type="text" name="username" placeholder="Username" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" class="btn-primary">Masuk (Login)</button>
        </form>
        
        <div style="text-align: center; margin-top: 16px; font-size: 13px;">
            Belum punya akun? <a href="/register" style="color: var(--accent-color); text-decoration: none; font-weight:600;">Daftar di sini</a>
        </div>
    </div>
{% elif request.path == '/register' and not session.get('username') %}
    <!-- HALAMAN REGISTER -->
    <div class="auth-container">
        <h2>📝 Buat Akun Baru</h2>
        {% if error %}
            <div class="error-msg">{{ error }}</div>
        {% endif %}
        <form action="/register" method="POST">
            <input type="text" name="username" placeholder="Username Baru" required>
            <input type="password" name="password" placeholder="Password" required>
            <button type="submit" class="btn-primary">Daftar Akun</button>
        </form>
        <div style="text-align: center; margin-top: 16px; font-size: 13px;">
            Sudah punya akun? <a href="/" style="color: var(--accent-color); text-decoration: none; font-weight:600;">Login</a>
        </div>
    </div>
{% else %}
    <!-- HALAMAN UTAMA ITINERARY (SETELAH LOGIN) -->
    <div class="mac-window">
        <div class="window-header">
            <div class="window-dots">
                <div class="dot dot-close"></div>
                <div class="dot dot-min"></div>
                <div class="dot dot-max"></div>
            </div>
            <div class="window-title">Gwangju_Itinerary_MultiUser.app</div>
        </div>
        <div class="content-body">
            <div class="top-nav">
                <div>Halo, <b>{{ session.get('username') }}</b>! 👋</div>
                <a href="/logout" class="logout-link">Keluar (Logout)</a>
            </div>

            <h2>🇰🇷 Gwangju Weekend Trip</h2>
            <div class="subtitle">Kelola rencana perjalanan privat Anda</div>

            <!-- Form Tambah Itinerary -->
            <div class="add-form">
                <h3 style="margin:0 0 10px 0; font-size:14px; color:var(--accent-color);">➕ Tambah Destinasi Baru</h3>
                <form action="/add" method="POST">
                    <div class="form-grid">
                        <input type="text" name="day" placeholder="Hari (Contoh: Day 1)" required>
                        <input type="text" name="time" placeholder="Waktu (Contoh: 10:00 - 12:00)" required>
                        <input type="text" name="place" placeholder="Nama Tempat" style="grid-column: span 2;" required>
                        <input type="text" name="category" placeholder="Kategori (Contoh: Kuliner)" required>
                        <input type="text" name="desc" placeholder="Deskripsi singkat" style="grid-column: span 2;" required>
                    </div>
                    <button type="submit" class="btn-primary" style="margin-top:4px;">Simpan Itinerary</button>
                </form>
            </div>

            <!-- Daftar List Itinerary Milik User yang Login -->
            {% for item in itinerary %}
            <div class="card {% if item[7] %}done{% endif %}">
                <form action="/toggle/{{ item[0] }}" method="POST" style="margin:0;">
                    <input type="checkbox" {% if item[7] %}checked{% endif %} onChange="this.form.submit()">
                </form>
                <div class="info">
                    <div class="day-tag">{{ item[2] }} • <span style="color:var(--text-muted);">{{ item[3] }}</span></div>
                    <div class="place-title">{{ item[4] }}</div>
                    <span class="badge">{{ item[5] }}</span>
                    <div class="desc">{{ item[6] }}</div>
                </div>
                <form action="/delete/{{ item[0] }}" method="POST" style="margin:0;">
                    <button type="submit" class="btn-delete" title="Hapus">✕</button>
                </form>
            </div>
            {% else %}
            <div style="text-align:center; color:var(--text-muted); padding: 20px;">Belum ada itinerary. Yuk tambah destinasi pertamamu!</div>
            {% endfor %}
        </div>
    </div>
{% endif %}

</body>
</html>
"""

@app.route("/")
def index():
    if "username" not in session:
        return render_template_string(HTML_TEMPLATE)
    
    # Ambil data itinerary khusus user yang sedang login
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM itineraries WHERE username = ?", (session["username"],))
    itinerary = cursor.fetchall()
    conn.close()
    
    return render_template_string(HTML_TEMPLATE, itinerary=itinerary)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username").strip()
        password = request.form.get("password").strip()
        
        if not username or not password:
            return render_template_string(HTML_TEMPLATE, error="Username dan password wajib diisi!")
            
        hashed_pw = generate_password_hash(password)
        try:
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_pw))
            conn.commit()
            conn.close()
            
            # Berikan data default pertama kali daftar
            conn = sqlite3.connect(DB_NAME)
            cursor = conn.cursor()
            default_items = [
                (username, "Day 1", "09:30 - 12:00", "Gwangju Art Street", "Culture & Art", "Menyusuri jalanan seni dan galeri.", 0),
                (username, "Day 1", "12:00 - 13:30", "Yangrim-dong History Village", "History", "Eksplorasi desa bersejarah.", 0)
            ]
            cursor.executemany("INSERT INTO itineraries (username, day, time, place, category, desc, done) VALUES (?, ?, ?, ?, ?, ?, ?)", default_items)
            conn.commit()
            conn.close()
            
            return render_template_string(HTML_TEMPLATE, success="Pendaftaran berhasil! Silakan login.")
        except sqlite3.IntegrityError:
            return render_template_string(HTML_TEMPLATE, error="Username sudah digunakan, pilih yang lain!")
            
    return render_template_string(HTML_TEMPLATE)

@app.route("/login", methods=["POST"])
def login():
    username = request.form.get("username").strip()
    password = request.form.get("password").strip()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    user = cursor.fetchone()
    conn.close()
    
    if user and check_password_hash(user[0], password):
        session["username"] = username
        return redirect(url_for("index"))
    else:
        return render_template_string(HTML_TEMPLATE, error="Username atau password salah!")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("index"))

@app.route("/add", methods=["POST"])
def add_item():
    if "username" not in session:
        return redirect(url_for("index"))
        
    username = session["username"]
    day = request.form.get("day")
    time = request.form.get("time")
    place = request.form.get("place")
    category = request.form.get("category")
    desc = request.form.get("desc")
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT INTO itineraries (username, day, time, place, category, desc, done) VALUES (?, ?, ?, ?, ?, ?, 0)",
                   (username, day, time, place, category, desc))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/toggle/<int:item_id>", methods=["POST"])
def toggle(item_id):
    if "username" not in session:
        return redirect(url_for("index"))
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT done FROM itineraries WHERE id = ? AND username = ?", (item_id, session["username"]))
    row = cursor.fetchone()
    if row:
        new_status = 0 if row[0] == 1 else 1
        cursor.execute("UPDATE itineraries SET done = ? WHERE id = ?", (new_status, item_id))
        conn.commit()
    conn.close()
    return redirect(url_for("index"))

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    if "username" not in session:
        return redirect(url_for("index"))
        
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM itineraries WHERE id = ? AND username = ?", (item_id, session["username"]))
    conn.commit()
    conn.close()
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
