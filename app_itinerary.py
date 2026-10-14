from flask import Flask, render_template_string, request, redirect, url_for
import os
import json

app = Flask(__name__)

# File JSON lokal untuk menyimpan data secara dinamis
DATA_FILE = "itinerary_data.json"

# Data Default jika file JSON belum ada
DEFAULT_DATA = [
    {"id": 1, "day": "Day 1", "time": "09:30 - 12:00", "place": "Gwangju Art Street (예술의거리)", "category": "Culture & Art", "desc": "Menyusuri jalanan seni, galeri lukisan, dan toko antik.", "done": False},
    {"id": 2, "day": "Day 1", "time": "12:00 - 13:30", "place": "Yangrim-dong History Village & Lunch", "category": "History & Food", "desc": "Eksplorasi desa bersejarah dan kuliner siang.", "done": False},
    {"id": 3, "day": "Day 1", "time": "14:00 - 17:00", "place": "Asia Culture Center (ACC)", "category": "Modern Culture", "desc": "Pameran seni interaktif dan rooftop garden yang luas.", "done": False},
    {"id": 4, "day": "Day 1", "time": "18:00 - Selesai", "place": "1913 Songjeong Station Market", "category": "Night Market", "desc": "Berburu jajanan malam dan Tteokgalbi khas Gwangju.", "done": False},
    {"id": 5, "day": "Day 2", "time": "09:00 - 12:00", "place": "Mudeungsu National Park & Jeungsimsa", "category": "Nature", "desc": "Trekking ringan dan kunjungi kuil asri di tengah hutan.", "done": False},
    {"id": 6, "day": "Day 2", "time": "12:30 - 14:00", "place": "Local Cafe Hopping", "category": "Relax", "desc": "Menikmati kopi di kafe nyaman sekitar Gwangju.", "done": False},
    {"id": 7, "day": "Day 2", "time": "14:30 - 17:00", "place": "Gwangju Lake Eco Park", "category": "Nature & Healing", "desc": "Jalan setapak di tepi danau dan jajaran pohon metasequoia.", "done": False}
]

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_DATA

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

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
        .dot {
            width: 12px;
            height: 12px;
            border-radius: 50%;
        }
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
        .content-body {
            padding: 24px;
        }
        h2 {
            margin: 0 0 4px 0;
            font-size: 22px;
            font-weight: 700;
            letter-spacing: -0.5px;
        }
        .subtitle {
            color: var(--text-muted);
            font-size: 13px;
            margin-bottom: 20px;
        }
        /* Form Tambah Destinasi */
        .add-form {
            background: #FAFAFC;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 16px;
            margin-bottom: 24px;
        }
        .add-form h3 {
            margin: 0 0 12px 0;
            font-size: 14px;
            font-weight: 600;
            color: var(--accent-color);
        }
        .form-grid {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }
        .form-grid full {
            grid-column: span 2;
        }
        input, select, textarea {
            width: 100%;
            padding: 8px 12px;
            border: 1px solid var(--border-color);
            border-radius: 6px;
            font-size: 13px;
            box-sizing: border-box;
            background: #FFFFFF;
            color: var(--text-color);
        }
        button.btn-add {
            background: var(--accent-color);
            color: white;
            border: none;
            padding: 10px;
            border-radius: 6px;
            font-weight: 600;
            font-size: 13px;
            cursor: pointer;
            width: 100%;
            margin-top: 10px;
        }
        button.btn-add:hover {
            opacity: 0.9;
        }
        /* Card Itinerary */
        .card {
            background: #FAFAFC;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
            display: flex;
            align-items: flex-start;
            gap: 14px;
            position: relative;
        }
        .card.done {
            opacity: 0.5;
            background: #F2F2F7;
        }
        .card.done .place-title {
            text-decoration: line-through;
            color: var(--text-muted);
        }
        input[type="checkbox"] {
            width: 20px;
            height: 20px;
            margin-top: 3px;
            accent-color: var(--accent-color);
            cursor: pointer;
        }
        .info {
            flex-grow: 1;
        }
        .day-tag {
            font-size: 11px;
            font-weight: 700;
            color: #FF9500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            margin-bottom: 2px;
        }
        .place-title {
            font-size: 15px;
            font-weight: 600;
            margin: 2px 0 6px 0;
        }
        .badge {
            display: inline-block;
            background: #EBF5FF;
            color: var(--accent-color);
            font-size: 10px;
            font-weight: 600;
            padding: 2px 8px;
            border-radius: 4px;
            margin-bottom: 6px;
        }
        .desc {
            font-size: 13px;
            color: #3A3A3C;
            line-height: 1.4;
        }
        .btn-delete {
            background: transparent;
            border: none;
            color: var(--danger-color);
            font-size: 16px;
            cursor: pointer;
            padding: 0 4px;
        }
        @media (max-width: 600px) {
            body { padding: 0; }
            .mac-window { border-radius: 0; border: none; box-shadow: none; }
            .form-grid { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="mac-window">
        <div class="window-header">
            <div class="window-dots">
                <div class="dot dot-close"></div>
                <div class="dot dot-min"></div>
                <div class="dot dot-max"></div>
            </div>
            <div class="window-title">Gwangju_Itinerary_Dynamic.app</div>
        </div>
        <div class="content-body">
            <h2>🇰🇷 Gwangju Weekend Trip</h2>
            <div class="subtitle">Tambah dan kelola rencana perjalanan liburanmu secara dinamis</div>

            <!-- Form Tambah Itinerary -->
            <div class="add-form">
                <h3>➕ Tambah Destinasi / Kegiatan Baru</h3>
                <form action="/add" method="POST">
                    <div class="form-grid">
                        <input type="text" name="day" placeholder="Hari (Contoh: Day 1 / Day 3)" required>
                        <input type="text" name="time" placeholder="Waktu (Contoh: 10:00 - 12:00)" required>
                        <input type="text" name="place" placeholder="Nama Tempat / Kegiatan" style="grid-column: span 2;" required>
                        <input type="text" name="category" placeholder="Kategori (Contoh: Kuliner / Nature)" required>
                        <input type="text" name="desc" placeholder="Deskripsi singkat kegiatan" style="grid-column: span 2;" required>
                    </div>
                    <button type="submit" class="btn-add">Simpan ke Itinerary</button>
                </form>
            </div>

            <!-- Daftar List Itinerary -->
            {% for item in itinerary %}
            <div class="card {% if item.done %}done{% endif %}">
                <form action="/toggle/{{ item.id }}" method="POST" style="margin:0;">
                    <input type="checkbox" {% if item.done %}checked{% endif %} onChange="this.form.submit()">
                </form>
                <div class="info">
                    <div class="day-tag">{{ item.day }} • <span style="color:var(--text-muted);">{{ item.time }}</span></div>
                    <div class="place-title">{{ item.place }}</div>
                    <span class="badge">{{ item.category }}</span>
                    <div class="desc">{{ item.desc }}</div>
                </div>
                <form action="/delete/{{ item.id }}" method="POST" style="margin:0;">
                    <button type="submit" class="btn-delete" title="Hapus">✕</button>
                </form>
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    itinerary_data = load_data()
    return render_template_string(HTML_TEMPLATE, itinerary=itinerary_data)

@app.route("/add", methods=["POST"])
def add_item():
    itinerary_data = load_data()
    new_id = max([item["id"] for item in itinerary_data], default=0) + 1
    
    new_entry = {
        "id": new_id,
        "day": request.form.get("day"),
        "time": request.form.get("time"),
        "place": request.form.get("place"),
        "category": request.form.get("category"),
        "desc": request.form.get("desc"),
        "done": False
    }
    itinerary_data.append(new_entry)
    save_data(itinerary_data)
    return redirect(url_for("index"))

@app.route("/toggle/<int:item_id>", methods=["POST"])
def toggle(item_id):
    itinerary_data = load_data()
    for item in itinerary_data:
        if item["id"] == item_id:
            item["done"] = not item["done"]
    save_data(itinerary_data)
    return redirect(url_for("index"))

@app.route("/delete/<int:item_id>", methods=["POST"])
def delete_item(item_id):
    itinerary_data = load_data()
    itinerary_data = [item for item in itinerary_data if item["id"] != item_id]
    save_data(itinerary_data)
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
