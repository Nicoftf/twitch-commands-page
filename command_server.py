from flask import Flask, render_template, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# --- DATENBANK-KONFIGURATION ---
# Lade die Datenbank-URL und den API-Schlüssel aus den Umgebungsvariablen
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # Spart Ressourcen
API_KEY = os.environ.get('COMMANDS_API_KEY')

# Initialisiere die Datenbank-Verbindung
db = SQLAlchemy(app)

# --- DATENBANK-MODELL (die Struktur der Tabelle) ---
# So sieht ein Eintrag in unserer Datenbanktabelle aus.
class Command(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True, nullable=False)
    response = db.Column(db.String(500), nullable=False)

    def to_dict(self):
        """Wandelt das Command-Objekt in ein Dictionary um."""
        return {self.name: {"response": self.response}}

# --- ROUTEN FÜR DIE WEBSEITE ---

@app.route('/')
def index():
    """Zeigt die befehle.html Seite an."""
    return render_template('befehle.html')

@app.route('/commands')
def get_commands():
    """Liest alle Befehle aus der Datenbank und gibt sie als JSON zurück."""
    commands = Command.query.all()
    # Wandle die Liste von Objekten in das gewohnte Dictionary-Format um
    command_dict = {}
    for cmd in commands:
        command_dict.update(cmd.to_dict())
    return jsonify(command_dict)

# --- ROUTEN FÜR DIE API (den Bot) ---

@app.route('/api/commands', methods=['POST'])
def add_command_api():
    """API-Endpunkt, um einen Befehl in der Datenbank zu speichern."""
    if request.headers.get('Authorization') != f'Bearer {API_KEY}':
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    command_name = data.get('name')
    command_response = data.get('response')

    if not command_name or not command_response:
        return jsonify({"error": "Missing name or response"}), 400

    # Prüfen, ob der Befehl schon existiert
    if Command.query.filter_by(name=command_name).first():
        return jsonify({"error": "Command already exists"}), 409

    # Neuen Befehl erstellen und in der Datenbank speichern
    new_command = Command(name=command_name, response=command_response)
    db.session.add(new_command)
    db.session.commit()

    return jsonify({"success": True, "command": command_name}), 201

@app.route('/api/commands/<path:command_name>', methods=['DELETE'])
def delete_command_api(command_name):
    """API-Endpunkt, um einen Befehl aus der Datenbank zu löschen."""
    if request.headers.get('Authorization') != f'Bearer {API_KEY}':
        return jsonify({"error": "Unauthorized"}), 401

    if not command_name.startswith('!'):
        command_name = '!' + command_name

    command_to_delete = Command.query.filter_by(name=command_name).first()

    if command_to_delete:
        db.session.delete(command_to_delete)
        db.session.commit()
        return jsonify({"success": True, "command_deleted": command_name}), 200
    else:
        return jsonify({"error": "Command not found"}), 404

# Diese Funktion sorgt dafür, dass die Tabelle "command" erstellt wird,
# wenn die App zum ersten Mal startet.
with app.app_context():
    db.create_all()