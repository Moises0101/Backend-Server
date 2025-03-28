from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

def get_db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="login_system"
    )

# 👇 ADD THIS ROUTE TO TEST SERVER IS UP
@app.route('/')
def home():
    return "Hello from Flask!"

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify(success=False, message="Invalid input"), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (data['username'], data['password']))
        conn.commit()
        return jsonify(success=True, message="User registered successfully")
    except mysql.connector.Error as e:
        print("❌ MySQL Error:", e)
        return jsonify(success=False, message="Username already exists or database error"), 500
    finally:
        cursor.close()
        conn.close()

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    if not data or 'username' not in data or 'password' not in data:
        return jsonify(success=False, message="Invalid input"), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (data['username'], data['password']))
    user = cursor.fetchone()
    cursor.close()
    conn.close()

    if user:
        return jsonify(success=True, message="Login successful")
    else:
        return jsonify(success=False, message="Invalid username or password")

if __name__ == "__main__":
    app.run(port=8000)