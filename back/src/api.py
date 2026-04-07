from flask import Flask, jsonify, request
from flask_cors import CORS
from datetime import date, timedelta

import mariadb
import os
import hashlib
import secrets

conn = mariadb.connect(
    user="user",
    password=os.getenv("MYSQL_PASSWORD"),
    host="db",
    port=3306,
    database="frum",
)
cursor = conn.cursor()

app = Flask(__name__)
CORS(app)


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "Internal server error"}), 500

    try:
        cursor.execute(
            "SELECT passwordHash, salt, id FROM users WHERE username = ?",
            (data["username"],),
        )
        row = cursor.fetchone()

        if row is None:
            return jsonify({"error": "Wrong Username or Password"}), 403

        hashed = hashlib.sha256((data["password"] + row[1]).encode()).hexdigest()
        if row[0] == hashed:
            token = generateToken(row[2])
            if token is None:
                return jsonify({"error": "Internal server error"}), 500

            return jsonify({"token": token})
        else:
            return jsonify({"error": "Wrong Username or Password"}), 403
    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data or "username" not in data or "password" not in data:
        return jsonify({"error": "username and password are required"}), 400

    try:
        cursor.execute("SELECT id FROM users WHERE username = ?", (data["username"],))
        if cursor.fetchone() is not None:
            return jsonify({"error": "Username already taken"}), 409

        salt = secrets.token_hex(16)
        hashed = hashlib.sha256((data["password"] + salt).encode()).hexdigest()

        cursor.execute(
            "INSERT INTO users (username, passwordHash, salt) VALUES (?, ?, ?)",
            (data["username"], hashed, salt),
        )
        conn.commit()

        cursor.execute("SELECT id FROM users WHERE username = ?", (data["username"],))
        new_user = cursor.fetchone()

        token = generateToken(new_user[0])
        if token is None:
            return jsonify({"error": "Internal server error"}), 500

        return jsonify({"token": token}), 201

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


@app.route("/session", methods=["POST"])
def session():
    data = request.get_json()

    if not data or "token" not in data:
        return jsonify({"error": "Token is required"}), 400

    try:
        # Chercher le token dans la table sessions
        cursor.execute(
            "SELECT user_id, expiration FROM sessions WHERE token = ?", (data["token"],)
        )
        row = cursor.fetchone()

        if row is None:
            return jsonify({"error": "Invalid token"}), 403

        user_id = row[0]
        expiration = row[1]

        if date.today() > expiration:

            cursor.execute("DELETE FROM sessions WHERE token = ?", (data["token"],))
            conn.commit()
            return jsonify({"error": "Session expired"}), 403

        # Récupérer les infos de l'utilisateur lié à ce token
        cursor.execute("SELECT id, username FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()

        return jsonify({"user_id": user[0], "username": user[1]}), 200

    except Exception:
        return jsonify({"error": "Internal server error"}), 500


def generateToken(userid):
    try:
        token = secrets.token_urlsafe(32)
        expiration = date.today() + timedelta(days=10)
        cursor.execute(
            "INSERT INTO sessions (user_id, token, expiration) VALUES (?, ?, ?)",
            (userid, token, expiration),
        )
        conn.commit()
        return token
    except Exception:
        return None


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
