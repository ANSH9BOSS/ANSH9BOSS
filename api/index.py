import os
import json
from pathlib import Path
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_PATH = DATA_DIR / "config.json"

# Vercel serverless has a read-only filesystem except for /tmp
IS_VERCEL = "VERCEL" in os.environ
if IS_VERCEL:
    SCANS_FILE = Path("/tmp/scans.json")
    DETECTIONS_FILE = Path("/tmp/detections.json")
    HASHES_FILE = Path("/tmp/verified_hashes.json")
    CONFIG_FILE = Path("/tmp/config.json")
else:
    SCANS_FILE = DATA_DIR / "scans.json"
    DETECTIONS_FILE = DATA_DIR / "detections.json"
    HASHES_FILE = DATA_DIR / "verified_hashes.json"
    CONFIG_FILE = CONFIG_PATH

# Configure relative template and static paths for Vercel
app = Flask(__name__, template_folder='../web/templates', static_folder='../web/static')
app.secret_key = "ansh9boss_super_secret_session_key_2026"

ADMIN_PASSCODE = os.environ.get("ANSH9BOSS_ADMIN_PASSCODE", "ansh9boss2026")

# JSON File Read/Write Helpers
def read_json_file(file_path, default_value):
    if not file_path.exists():
        return default_value
    try:
        with open(file_path, "r") as f:
            return json.load(f)
    except Exception:
        return default_value

def write_json_file(file_path, data):
    try:
        file_path.parent.mkdir(exist_ok=True)
        with open(file_path, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Error writing to {file_path}: {e}")

def load_config():
    """Load configuration from config.json with fallback default."""
    default_config = {
        "version": "1.0.0",
        "known_cheats": [
            "wurst", "meteor", "sigma", "impact", "aristois", "future", "liquidbounce", 
            "wolfram", "inertia", "ares", "sentry", "entropy", "reflex", "bleach", 
            "ancientaura", "killaura", "huzuni", "nodus", "vape", "badlion", "mathax",
            "kamiblue", "kami", "salhack", "rusherhack"
        ],
        "known_packages": [
            "meteorclient", "wurst", "sigma", "future", "liquidbounce", "mathax", 
            "ares", "wolfram", "kamiblue", "salhack", "rusherhack", "aristois", "huzuni", "vape"
        ],
        "cheat_strings": [
            "aimbot", "killaura", "esp", "wallhack", "xray", "freecam", 
            "nofall", "scaffold", "triggerbot", "autoclick", "baritone", "pathfind", 
            "autototem", "fastplace", "criticals", "antiknockback", "nuker", 
            "jesus", "automine", "cheatengine"
        ]
    }
    
    # On Vercel, seed /tmp/config.json from local config.json if not present
    if IS_VERCEL and not CONFIG_FILE.exists() and CONFIG_PATH.exists():
        try:
            with open(CONFIG_PATH, "r") as f:
                write_json_file(CONFIG_FILE, json.load(f))
        except Exception:
            pass
            
    return read_json_file(CONFIG_FILE, default_config)

def save_config(config_data):
    """Save configuration."""
    write_json_file(CONFIG_FILE, config_data)
    if not IS_VERCEL and CONFIG_FILE != CONFIG_PATH:
        write_json_file(CONFIG_PATH, config_data)

def get_all_scans():
    return read_json_file(SCANS_FILE, [])

def save_scans(scans):
    write_json_file(SCANS_FILE, scans)

def get_all_detections():
    return read_json_file(DETECTIONS_FILE, [])

def save_detections(detections):
    write_json_file(DETECTIONS_FILE, detections)

def get_all_hashes():
    return read_json_file(HASHES_FILE, {})

def save_hashes(hashes):
    write_json_file(HASHES_FILE, hashes)

def get_stats():
    """Aggregate statistics from JSON files."""
    scans = get_all_scans()
    detections = get_all_detections()
    
    total_scans = len(scans)
    total_files_scanned = sum(s.get("total_files", 0) for s in scans)
    total_flagged_files = sum(s.get("flagged_files", 0) for s in scans)
    
    # Layers Breakdown
    detection_layers = {}
    for d in detections:
        layer = d.get("detection_layer", "Unknown")
        detection_layers[layer] = detection_layers.get(layer, 0) + 1
        
    # Common Threats
    threat_counts = {}
    for d in detections:
        key = (d.get("file_name"), d.get("risk_level", "SUSPICIOUS"))
        if key[0]:
            threat_counts[key] = threat_counts.get(key, 0) + 1
        
    # Sort and format top 5
    sorted_threats = sorted(threat_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    common_threats = [
        {"file_name": k[0], "risk_level": k[1], "count": v}
        for k, v in sorted_threats
    ]
    
    # Recent Scans (sorted descending)
    recent_scans = list(reversed(scans))[:15]
    
    return {
        "total_scans": total_scans,
        "total_files_scanned": total_files_scanned,
        "total_flagged_files": total_flagged_files,
        "detection_layers": detection_layers,
        "common_threats": common_threats,
        "recent_scans": recent_scans
    }

@app.route("/download/ansh9boss.apk")
def download_apk():
    apk_path = BASE_DIR / "web" / "static" / "ansh9boss.apk"
    if not apk_path.exists():
        return render_template("apk_placeholder.html")
    from flask import send_from_directory
    return send_from_directory(os.path.join(app.root_path, '../web/static'), 'ansh9boss.apk', as_attachment=True)

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
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "message": "No payload received"}), 400
            
        platform = data.get("platform", "Unknown")
        total_files = data.get("total_files", 0)
        flagged_files = data.get("flagged_files", 0)
        highest_risk = data.get("highest_risk", "CLEAN")
        detections = data.get("detections", [])
        
        scans = get_all_scans()
        new_scan_id = len(scans) + 1
        
        timestamp_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        scan_record = {
            "id": new_scan_id,
            "timestamp": timestamp_str,
            "total_files": total_files,
            "flagged_files": flagged_files,
            "highest_risk": highest_risk,
            "platform": platform
        }
        scans.append(scan_record)
        save_scans(scans)
        
        all_detections = get_all_detections()
        for det in detections:
            new_det_id = len(all_detections) + 1
            det_record = {
                "id": new_det_id,
                "scan_id": new_scan_id,
                "file_name": det.get("file_name"),
                "file_path": "Telemetry Upload (Anonymized)",
                "risk_level": det.get("risk_level"),
                "detection_layer": det.get("detection_layer"),
                "matched_details": ", ".join(det.get("matched_details")) if isinstance(det.get("matched_details"), list) else det.get("matched_details")
            }
            all_detections.append(det_record)
        save_detections(all_detections)
            
        return jsonify({"success": True, "message": "Global telemetry logged successfully!"})
    except Exception as e:
        return jsonify({"success": False, "message": f"Telemetry processing error: {str(e)}"}), 500

@app.route("/api/live_feed")
def live_feed():
    try:
        scans = get_all_scans()
        all_detections = get_all_detections()
        
        total_scans = len(scans)
        total_files = sum(s.get("total_files", 0) for s in scans)
        total_flagged = sum(s.get("flagged_files", 0) for s in scans)
        
        global_stats = {
            "total_scans": total_scans,
            "total_files": total_files,
            "total_flagged": total_flagged
        }
        
        scan_map = {s["id"]: s for s in scans}
        
        recent_detections = []
        for d in reversed(all_detections):
            if len(recent_detections) >= 8:
                break
            scan_id = d.get("scan_id")
            scan = scan_map.get(scan_id, {})
            
            recent_detections.append({
                "file_name": d.get("file_name"),
                "risk_level": d.get("risk_level"),
                "detection_layer": d.get("detection_layer"),
                "platform": scan.get("platform", "Unknown"),
                "timestamp": scan.get("timestamp", "")
            })
            
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

@app.route("/api/rules")
def get_rules():
    config = load_config()
    return jsonify({
        "version": config.get("version", "1.0.0"),
        "known_cheats": config.get("known_cheats", []),
        "known_packages": config.get("known_packages", []),
        "cheat_strings": config.get("cheat_strings", [])
    })

@app.route("/api/verify_hash")
def verify_hash():
    sha1 = request.args.get("hash", "").strip().lower()
    if not sha1 or len(sha1) != 40:
        return jsonify({"valid": False, "error": "Invalid SHA-1 hash"}), 400

    # Check local JSON cache
    hashes = get_all_hashes()
    if sha1 in hashes:
        cached = hashes[sha1]
        return jsonify({
            "valid": True,
            "hash": sha1,
            "clean": cached["clean"],
            "source": cached["source"],
            "cached": True
        })

    # Query Modrinth API
    import urllib.request
    import urllib.error
    url = f"https://api.modrinth.com/v2/version_file/{sha1}?algorithm=sha1"
    
    clean_mod = False
    source = "Unverified"
    
    try:
        req = urllib.request.Request(
            url,
            headers={'User-Agent': 'ANSH9BOSS-Validator/1.0 (contact@ansh9boss.app)'}
        )
        with urllib.request.urlopen(req, timeout=3) as resp:
            resp_data = json.loads(resp.read().decode("utf-8"))
            if "id" in resp_data:
                clean_mod = True
                source = "Modrinth Verified"
    except urllib.error.HTTPError as e:
        if e.code == 404:
            clean_mod = False
            source = "Modrinth Unknown (Unverified)"
        else:
            return jsonify({"valid": False, "error": f"Cloud API error: {e.reason}"}), 502
    except Exception as e:
        return jsonify({"valid": False, "error": f"Lookup failed: {str(e)}"}), 500

    # Save to local JSON cache
    hashes[sha1] = {
        "clean": clean_mod,
        "source": source,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    save_hashes(hashes)

    return jsonify({
        "valid": True,
        "hash": sha1,
        "clean": clean_mod,
        "source": source,
        "cached": False
    })

if __name__ == "__main__":
    # Create local data dir if not exists
    DATA_DIR.mkdir(exist_ok=True)
    app.run(host="0.0.0.0", port=5000, debug=True)
