from flask import Flask, render_template_string, request, redirect, url_for
import os

app = Flask(__name__)

# Data Itinerary Gwangju
itinerary_data = [
    # Day 1
    {"id": 1, "day": "Day 1", "time": "09:30 - 12:00", "place": "Gwangju Art Street (예술의거리)", "category": "Culture & Art", "desc": "Menyusuri jalanan seni, galeri lukisan, dan toko antik.", "done": False},
    {"id": 2, "day": "Day 1", "time": "12:00 - 13:30", "place": "Yangrim-dong History Village & Lunch", "category": "History & Food", "desc": "Eksplorasi desa bersejarah dan kuliner siang.", "done": False},
    {"id": 3, "day": "Day 1", "time": "14:00 - 17:00", "place": "Asia Culture Center (ACC)", "category": "Modern Culture", "desc": "Pameran seni interaktif dan rooftop garden yang luas.", "done": False},
    {"id": 4, "day": "Day 1", "time": "18:00 - Selesai", "place": "1913 Songjeong Station Market", "category": "Night Market", "desc": "Berburu jajanan malam dan Tteokgalbi khas Gwangju.", "done": False},
    
    # Day 2
    {"id": 5, "day": "Day 2", "time": "09:00 - 12:00", "place": "Mudeungsu National Park & Jeungsimsa", "category": "Nature", "desc": "Trekking ringan dan kunjungi kuil asri di tengah hutan.", "done": False},
    {"id": 6, "day": "Day 2", "time": "12:30 - 14:00", "place": "Local Cafe Hopping", "category": "Relax", "desc": "Menikmati kopi di kafe nyaman sekitar Gwangju.", "done": False},
    {"id": 7, "day": "Day 2", "time": "14:30 - 17:00", "place": "Gwangju Lake Eco Park", "category": "Nature & Healing", "desc": "Jalan setapak di tepi danau dan jajaran pohon metasequoia.", "done": False}
]

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
            max-width: 680px;
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
        .card {
            background: #FAFAFC;
            border: 1px solid var(--border-color);
            border-radius: 10px;
            padding: 14px 16px;
            margin-bottom: 12px;
            display: flex;
            align-items: flex-start;
            gap: 14px;
            transition: all 0.2s ease;
        }
        .card:hover {
            border-color: var(--accent-color);
            box-shadow: 0 4px 12px rgba(0, 122, 255, 0.06);
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
        @media (max-width: 600px) {
            body { padding: 0; }
            .mac-window { border-radius: 0; border: none; box-shadow: none; }
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
            <div class="window-title">Gwangju_Itinerary.app</div>
        </div>
        <div class="content-body">
            <h2>🇰🇷 Gwangju Weekend Trip</h2>
            <div class="subtitle">Rencana perjalanan santai & healing di Gwangju</div>

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
            </div>
            {% endfor %}
        </div>
    </div>
</body>
</html>
"""

@app.route("/")
def index():
    return render_template_string(HTML_TEMPLATE, itinerary=itinerary_data)

@app.route("/toggle/<int:item_id>", methods=["POST"])
def toggle(item_id):
    for item in itinerary_data:
        if item["id"] == item_id:
            item["done"] = not item["done"]
    return redirect(url_for("index"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)