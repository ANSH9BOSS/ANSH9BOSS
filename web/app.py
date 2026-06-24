import os
import json
import sqlite3
from pathlib import Path
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_PATH = DATA_DIR / "config.json"
DB_PATH = DATA_DIR / "ansh9boss_global.db"

app = Flask(__name__)
app.secret_key = "ansh9boss_super_secret_session_key_2026"

# Default passcode for admin
ADMIN_PASSCODE = os.environ.get("ANSH9BOSS_ADMIN_PASSCODE", "ansh9boss2026")

def load_config():
    """Load configuration from config.json."""
    if not CONFIG_PATH.exists():
        return {
            "version": "1.0.0",
            "known_cheats": [],
            "known_packages": [],
            "cheat_strings": []
        }
    with open(CONFIG_PATH, "r") as f:
        return json.load(f)

def save_config(config_data):
    """Save configuration to config.json."""
    DATA_DIR.mkdir(exist_ok=True)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config_data, f, indent=2)

def init_db():
    """Ensure SQLite DB and tables exist with correct schema (including platform)."""
    DATA_DIR.mkdir(exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS scans (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        total_files INTEGER,
        flagged_files INTEGER,
        highest_risk TEXT,
        platform TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS detections (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        scan_id INTEGER,
        file_name TEXT,
        file_path TEXT,
        risk_level TEXT,
        detection_layer TEXT,
        matched_details TEXT,
        FOREIGN KEY(scan_id) REFERENCES scans(id)
    )
    """)
    
    conn.commit()
    conn.close()

def get_stats():
    """Query statistics from local/global database."""
    init_db()
    stats = {
        "total_scans": 0,
        "total_files_scanned": 0,
        "total_flagged_files": 0,
        "detection_layers": {},
        "common_threats": [],
        "recent_scans": []
    }
    
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Scans summary
        cursor.execute("SELECT COUNT(*) as total_scans, SUM(total_files) as total_files, SUM(flagged_files) as total_flagged FROM scans")
        row = cursor.fetchone()
        if row and row["total_scans"] > 0:
            stats["total_scans"] = row["total_scans"]
            stats["total_files_scanned"] = row["total_files"] or 0
            stats["total_flagged_files"] = row["total_flagged"] or 0
            
        # Layers breakdown
        cursor.execute("SELECT detection_layer, COUNT(*) as count FROM detections GROUP BY detection_layer")
        for r in cursor.fetchall():
            layer_name = r["detection_layer"] or "Unknown"
            stats["detection_layers"][layer_name] = r["count"]
            
        # Common threat files
        cursor.execute("SELECT file_name, risk_level, COUNT(*) as count FROM detections GROUP BY file_name ORDER BY count DESC LIMIT 5")
        stats["common_threats"] = [dict(r) for r in cursor.fetchall()]
        
        # Recent scans list (global)
        cursor.execute("SELECT id, timestamp, total_files, flagged_files, highest_risk, platform FROM scans ORDER BY timestamp DESC LIMIT 15")
        stats["recent_scans"] = [dict(r) for r in cursor.fetchall()]
        
        conn.close()
    except Exception as e:
        print(f"Error fetching stats: {e}")
        
    return stats

@app.route("/")
def index():
    config = load_config()
    return render_template("index.html", version=config.get("version", "1.0.0"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if session.get("admin_logged_in"):
        return redirect(url_for("admin"))
        
    if request.method == "POST":
        passcode = request.form.get("passcode")
        if passcode == ADMIN_PASSCODE:
            session["admin_logged_in"] = True
            return redirect(url_for("admin"))
        else:
            flash("Invalid admin passcode! Please try again.", "error")
            
    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("admin_logged_in"):
        return redirect(url_for("login"))
        
    stats = get_stats()
    config = load_config()
    return render_template("admin.html", stats=stats, config=config)

@app.route("/logout")
def logout():
    session.pop("admin_logged_in", None)
    return redirect(url_for("index"))

@app.route("/api/report_scan", methods=["POST"])
def report_scan():
    """Public endpoint for scanners around the world to upload telemetry."""
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No payload received"}), 400
            
        platform = data.get("platform", "Unknown")
        total_files = data.get("total_files", 0)
        flagged_files = data.get("flagged_files", 0)
        highest_risk = data.get("highest_risk", "CLEAN")
        detections = data.get("detections", [])
        
        init_db()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO scans (total_files, flagged_files, highest_risk, platform) VALUES (?, ?, ?, ?)",
            (total_files, flagged_files, highest_risk, platform)
        )
        scan_id = cursor.lastrowid
        
        for det in detections:
            cursor.execute(
                """INSERT INTO detections 
                   (scan_id, file_name, file_path, risk_level, detection_layer, matched_details) 
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    scan_id,
                    det.get("file_name"),
                    "Telemetry Upload (Anonymized)",  # Hide client system absolute path
                    det.get("risk_level"),
                    det.get("detection_layer"),
                    ", ".join(det.get("matched_details")) if isinstance(det.get("matched_details"), list) else det.get("matched_details")
                )
            )
            
        conn.commit()
        conn.close()
        return jsonify({"success": True, "message": "Global telemetry logged successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Telemetry processing error: {str(e)}"}), 500

@app.route("/api/live_feed")
def live_feed():
    """Fetch global real-time counters and recent threat detections."""
    try:
        init_db()
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query total counters
        cursor.execute("SELECT COUNT(*) as scans, SUM(total_files) as files, SUM(flagged_files) as flagged FROM scans")
        stats_row = cursor.fetchone()
        
        global_stats = {
            "total_scans": stats_row["scans"] if stats_row else 0,
            "total_files": stats_row["files"] if stats_row and stats_row["files"] else 0,
            "total_flagged": stats_row["flagged"] if stats_row and stats_row["flagged"] else 0
        }
        
        # Query latest 8 flagged detections
        cursor.execute("""
            SELECT d.file_name, d.risk_level, d.detection_layer, s.platform, s.timestamp 
            FROM detections d
            JOIN scans s ON d.scan_id = s.id
            ORDER BY s.timestamp DESC LIMIT 8
        """)
        
        recent_detections = []
        for r in cursor.fetchall():
            recent_detections.append({
                "file_name": r["file_name"],
                "risk_level": r["risk_level"],
                "detection_layer": r["detection_layer"],
                "platform": r["platform"],
                "timestamp": r["timestamp"]
            })
            
        conn.close()
        return jsonify({
            "success": True,
            "stats": global_stats,
            "recent": recent_detections
        })
    except Exception as e:
        return jsonify({"success": False, "message": str(e)}), 500

@app.route("/api/update_config", methods=["POST"])
def update_config():
    if not session.get("admin_logged_in"):
        return jsonify({"success": False, "message": "Unauthorized"}), 401
        
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No data received"}), 400
            
        config = load_config()
        
        if "version" in data:
            config["version"] = data["version"].strip()
            
        if "known_cheats" in data:
            config["known_cheats"] = [x.strip().lower() for x in data["known_cheats"] if x.strip()]
            
        if "known_packages" in data:
            config["known_packages"] = [x.strip().lower() for x in data["known_packages"] if x.strip()]
            
        if "cheat_strings" in data:
            config["cheat_strings"] = [x.strip().lower() for x in data["cheat_strings"] if x.strip()]
            
        save_config(config)
        return jsonify({"success": True, "message": "Configuration updated successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Server error: {str(e)}"}), 500

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000, debug=True)
