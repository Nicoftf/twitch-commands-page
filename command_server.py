import json
from flask import Flask, jsonify, send_from_directory
from flask_cors import CORS

# --- Konfiguration ---
STATIC_COMMANDS = {
    "Allgemein": [
        {"name": "hallo", "description": "Begrüßt den Benutzer freundlich."},
        {"name": "info", "description": "Gibt eine kurze Info über den Bot aus."},
        {"name": "commands", "description": "Sendet den Link zu dieser Website"},
        {"name": "lurk", "description": "Lass den Chat wissen, dass du im Hintergrund zuschaust."},
        {"name": "rank", "description": "Zeigt den aktuellen Valorant-Rang von CandeCate an."},
        {"name": "smashorpass", "description": "Link zum Erstellen eines 'Smash or Pass'-Sets."},
        {"name": "boosted", "description": "Zählt, wie oft CandeCate als 'boosted' bezeichnet wurde."},
        {"name": "energy", "description": "Zählt die getrunkenen Energy-Dosen im Stream."},
        {"name": "wp", "description": "Zählt, wie oft CandeCates Plays gelobt wurden."},
        {"name": "v", "description": "Timeoute dich selber"}
    ],
    "Soziale Netzwerke": [
        {"name": "socials", "description": "Zeigt den Linktree mit allen wichtigen Links."},
        {"name": "twitter", "aliases": ["x"], "description": "Link zum Twitter/X-Profil."},
        {"name": "discord", "aliases": ["dc"], "description": "Link zum Discord-Server."},
        {"name": "instagram", "aliases": ["insta"], "description": "Link zum Instagram-Profil."},
        {"name": "tiktok", "description": "Link zum TikTok-Profil."},
        {"name": "youtube", "aliases": ["yt"], "description": "Link zum YouTube-Kanal."}
    ],
    "Stream-Informationen": [
        {"name": "uptime", "description": "Zeigt, wie lange der Stream bereits live ist."},
        {"name": "title", "description": "Zeigt den aktuellen Titel des Streams."},
        {"name": "game", "description": "Zeigt das aktuell gestreamte Spiel bzw. die Kategorie."},
        {"name": "song", "description": "Zeigt den aktuell auf Spotify laufenden Song an."},
        {"name": "followage", "description": "Zeigt wie lange du oder ein anderer Nutzer dem Kanal schon folgt."},
        {"name": "watchtime", "description": "Zeigt deine angesammelte Zuschauzeit im Kanal an."}
    ],
    "BonbonTaler (Währung)": [
        {"name": "bonbons", "aliases": ["taler", "bt", "balance", "konto"], "description": "Zeigt deinen Kontostand an BonbonTalern."},
        {"name": "gamble", "description": "Setze deine BonbonTaler bei einem Münzwurf."},
        {"name": "bestenliste", "description": "Zeigt die Top 5 Benutzer mit den meisten BonbonTalern."}
    ],
    "Moderations-Befehle": [
        {"name": "new", "description": "Erstellt einen neuen benutzerdefinierten Befehl.", "mod": True},
        {"name": "edit", "description": "Bearbeitet einen bestehenden benutzerdefinierten Befehl.", "mod": True},
        {"name": "del", "description": "Löscht einen benutzerdefinierten Befehl.", "mod": True},
        {"name": "addrandommsg", "description": "Fügt eine neue zeitgesteuerte Nachricht hinzu.", "mod": True},
        {"name": "delrandommsg", "description": "Löscht eine zeitgesteuerte Nachricht per Index.", "mod": True},
        {"name": "listrandommsgs", "description": "Listet alle zeitgesteuerten Nachrichten auf.", "mod": True},
        {"name": "shoutout", "aliases": ["so"], "description": "Gibt einem anderen Streamer einen Shoutout."},
    ]
}

COMMANDS_JSON_FILE = 'commands.json'
HTML_FILE_NAME = 'befehle.html'     

# --- Flask App ---
app = Flask(__name__)
CORS(app) 

def load_custom_commands():
    """Lädt die Befehle aus der commands.json Datei."""
    try:
        with open(COMMANDS_JSON_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
            return [{"name": name, "description": content} for name, content in data.items()]
    except (FileNotFoundError, json.JSONDecodeError):
        
        return []

@app.route('/')
def serve_html_page():
    """Diese Route liefert die Webseite (befehle.html) aus."""
    return send_from_directory('.', HTML_FILE_NAME)

@app.route('/commands')
def get_commands():
    """Der API-Endpunkt, der alle Befehle kombiniert und als JSON zurückgibt."""
    all_commands = STATIC_COMMANDS.copy()
    
    
    custom_commands = load_custom_commands()
    
    
    if custom_commands:
        all_commands["Benutzerdefinierte Befehle"] = custom_commands
    
    return jsonify(all_commands)

if __name__ == '__main__':
    
    app.run(host='0.0.0.0', port=5000, debug=False)