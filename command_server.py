from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
import os

COMMANDS = {}

app = Flask(__name__)
CORS(app)

API_KEY = os.environ.get('COMMANDS_API_KEY')

# --- ROUTEN FÜR DIE WEBSEITE ---

@app.route('/')
def index():
    """Zeigt die befehle.html Seite an."""
    return render_template('befehle.html')

@app.route('/commands')
def get_commands():
    """Liefert die Befehle aus dem Speicher als JSON."""
    return jsonify(COMMANDS)

# --- ROUTEN FÜR DIE API (den Bot) ---

@app.route('/api/commands', methods=['POST'])
def add_command_api():
    """API-Endpunkt, um einen neuen Befehl hinzuzufügen."""
    auth_header = request.headers.get('Authorization')
    if not API_KEY or not auth_header or auth_header != f'Bearer {API_KEY}':
        return jsonify({"error": "Unauthorized"}), 401

    data = request.json
    command_name = data.get('name')
    command_response = data.get('response')

    if not command_name or not command_response:
        return jsonify({"error": "Missing name or response"}), 400

    
    COMMANDS[command_name] = {"response": command_response}

    print(f"Befehl hinzugefügt: {command_name}. Aktuelle Befehle: {COMMANDS}") 
    return jsonify({"success": True, "command": command_name}), 201


@app.route('/api/commands/<path:command_name>', methods=['DELETE'])
def delete_command_api(command_name):
    """API-Endpunkt, um einen Befehl zu löschen."""
    auth_header = request.headers.get('Authorization')
    if not API_KEY or not auth_header or auth_header != f'Bearer {API_KEY}':
        return jsonify({"error": "Unauthorized"}), 401

    
    if not command_name.startswith('!'):
        command_name = '!' + command_name
    
    if command_name in COMMANDS:
        
        del COMMANDS[command_name]
        print(f"Befehl gelöscht: {command_name}. Aktuelle Befehle: {COMMANDS}") # Log für Debugging
        return jsonify({"success": True, "command_deleted": command_name}), 200
    else:
        return jsonify({"error": "Command not found"}), 404


if __name__ == '__main__':
    app.run(debug=True)