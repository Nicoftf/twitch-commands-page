from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# --- KONFIGURATION ---
# Wir fügen diese Zeile hinzu, um die alphabetische Sortierung zu deaktivieren.
app.config['JSON_SORT_KEYS'] = False

# Datenbank-Konfiguration mit lokalem Fallback
database_url = os.environ.get('DATABASE_URL')
if not database_url:
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'commands.db')
    database_url = f'sqlite:///{db_path}'
    print(f"INFO: DATABASE_URL nicht gesetzt. Fallback auf lokale DB: {database_url}")

app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

API_KEY = os.environ.get('COMMANDS_API_KEY', 'ein-geheimer-test-key')

# Initialisiere die Datenbank-Verbindung
db = SQLAlchemy(app)

class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    response = db.Column(db.String(500), nullable=False)

# --- ZENTRALE DEFINITION DER FESTEN BEFEHLE ---
# Die Reihenfolge hier wird jetzt dank der neuen Konfiguration beibehalten.
FIXED_COMMANDS = {
    "Allgemein": [
        {"name": "hallo", "description": "Begrüßt den Benutzer freundlich."},
        {"name": "info", "description": "Gibt eine kurze Info über den Bot aus."},
        {"name": "commands", "description": "Listet alle verfügbaren Befehle im Chat auf."},
        {"name": "lurk", "description": "Lass den Chat wissen, dass du im Hintergrund zuschaust."},
        {"name": "rank", "description": "Zeigt den aktuellen Valorant-Rang von CandeCate an."},
        {"name": "smashorpass", "description": "Link zum Erstellen eines 'Smash or Pass'-Sets."},
        {"name": "boosted", "description": "Zählt, wie oft CandeCate als 'boosted' bezeichnet wurde."},
        {"name": "energy", "description": "Zählt die getrunkenen Energy-Dosen im Stream."},
        {"name": "wp", "description": "Zählt, wie oft CandeCates 'Insane' Plays gelobt wurden."}
    ],
    "Soziale Netzwerke": [
        {"name": "socials", "description": "Zeigt den Linktree mit allen wichtigen Links."},
        {"name": "twitter", "description": "Link zum Twitter/X-Profil.", "aliases": ["x"]},
        {"name": "discord", "description": "Einladungslink zum Discord-Server.", "aliases": ["dc"]},
        {"name": "instagram", "description": "Link zum Instagram-Profil.", "aliases": ["insta"]},
        {"name": "tiktok", "description": "Link zum TikTok-Profil."},
        {"name": "youtube", "description": "Link zum YouTube-Kanal.", "aliases": ["yt"]}
    ],
    "BonbonTaler (Währung)": [
        {"name": "bonbons", "description": "Zeigt deinen Kontostand an BonbonTalern.",  "aliases": ["taler", "bt", "balance", "konto"]},
        {"name": "gamble", "description": "Setze deine BonbonTaler bei einem Münzwurf."},
        {"name": "bestenliste", "description": "Zeigt die Top 5 der Benutzer mit den meisten BonbonTalern an."}
    ],
    "Song-Befehle": [
        {"name": "song", "description": "Zeigt den aktuell auf Spotify laufenden Song an."}
    ],
    "Stream-Informationen": [
        {"name": "uptime", "description": "Zeigt, wie lange der Stream bereits live ist."},
        {"name": "title", "description": "Zeigt den aktuellen Titel des Streams."},
        {"name": "game", "description": "Zeigt das aktuell gestreamte Spiel bzw. die Kategorie."},
        {"name": "followage", "description": "Prüft, wie lange du oder ein anderer Nutzer dem Kanal schon folgt."},
        {"name": "watchtime", "description": "Zeigt deine angesammelte Zuschauzeit im Kanal an."}
    ],
    "Moderation": [
        {"name": "new", "description": "Fügt einen neuen Befehl hinzu.", "mod": True},
        {"name": "edit", "description": "Bearbeitet einen Befehl.", "mod": True},
        {"name": "del", "description": "Löscht einen Befehl.", "mod": True},
        {"name": "addrandommsg", "description": "Fügt eine neue zeitgesteuerte Nachricht hinzu.", "mod": True},
        {"name": "delrandommsg ", "description": "Löscht eine zeitgesteuerte Nachricht per Index.", "mod": True},
        {"name": "listrandommsgs", "description": "Listet alle zeitgesteuerten Nachrichten auf.", "mod": True},
        {"name": "shoutout", "description": "Gibt einem anderen Streamer einen Shoutout.", "mod": True, "aliases": ["so"]},
    ]
}

@app.route('/')
def index():
    return render_template('befehle.html')

@app.route('/commands')
def get_commands():
    categorized_commands = {k: list(v) for k, v in FIXED_COMMANDS.items()}
    
    try:
        custom_commands_from_db = Command.query.all()
        if custom_commands_from_db:
            if "Benutzerdefiniert" not in categorized_commands:
                categorized_commands["Benutzerdefiniert"] = []
            for cmd in custom_commands_from_db:
                categorized_commands["Benutzerdefiniert"].append({
                    "name": cmd.name.lstrip('!'),
                    "description": cmd.response,
                    "mod": False,
                    "aliases": []
                })
    except Exception as e:
        print(f"WARNUNG: Konnte nicht auf die Datenbank zugreifen: {e}")

    if "Moderation" in categorized_commands:
        mod_commands = categorized_commands.pop("Moderation")
        categorized_commands["Moderation"] = mod_commands

    return jsonify(categorized_commands)

# --- Der Rest der Datei bleibt gleich ---
# (API-Routen etc.)
@app.route('/api/commands', methods=['POST'])
def add_command_api():
    if request.headers.get('Authorization') != f'Bearer {API_KEY}':
        return jsonify({"error": "Unauthorized"}), 401
    data = request.json
    command_name, command_response = data.get('name'), data.get('response')
    if not command_name or not command_response:
        return jsonify({"error": "Missing name or response"}), 400
    if Command.query.filter_by(name=command_name).first():
        return jsonify({"error": "Command already exists"}), 409
    db.session.add(Command(name=command_name, response=command_response))
    db.session.commit()
    return jsonify({"success": True, "command": command_name}), 201

@app.route('/api/commands/<path:command_name>', methods=['DELETE'])
def delete_command_api(command_name):
    if request.headers.get('Authorization') != f'Bearer {API_KEY}':
        return jsonify({"error": "Unauthorized"}), 401
    if not command_name.startswith('!'): command_name = '!' + command_name
    command_to_delete = Command.query.filter_by(name=command_name).first()
    if command_to_delete:
        db.session.delete(command_to_delete)
        db.session.commit()
        return jsonify({"success": True, "command_deleted": command_name}), 200
    return jsonify({"error": "Command not found"}), 404
    
@app.route('/api/commands/<path:command_name>', methods=['PUT'])
def edit_command_api(command_name):
    if request.headers.get('Authorization') != f'Bearer {API_KEY}':
        return jsonify({"error": "Unauthorized"}), 401
    if not command_name.startswith('!'): command_name = '!' + command_name
    command_to_edit = Command.query.filter_by(name=command_name).first()
    if command_to_edit:
        data = request.json
        new_response = data.get('response')
        if not new_response: return jsonify({"error": "Missing new response"}), 400
        command_to_edit.response = new_response
        db.session.commit()
        return jsonify({"success": True, "command_edited": command_name}), 200
    return jsonify({"error": "Command not found"}), 404

with app.app_context():
    try:
        db.create_all()
    except Exception as e:
        print(f"WARNUNG: Konnte Datenbanktabellen nicht erstellen (ignoriere für lokale Tests): {e}")

if __name__ == '__main__':
    app.run(debug=True)