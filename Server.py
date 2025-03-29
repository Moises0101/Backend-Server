from flask import Flask, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import CORS  # Import CORS

print("🔹 MySQL Connector is installed and working!")

# Load environment variables from the .env file
if not load_dotenv():
    print("⚠️ Warning: .env file not found or failed to load!")

# Debugging: Print loaded environment variables
print("🔹 ENV VARIABLES CHECK")
print("🔹 MYSQL_HOST:", os.getenv('MYSQLHOST'))
print("🔹 MYSQL_PORT:", os.getenv('MYSQLPORT'))
print("🔹 MYSQL_USER:", os.getenv('MYSQLUSER'))
print("🔹 MYSQL_PASSWORD:", "********")  # Masked for security
print("🔹 MYSQL_DATABASE:", os.getenv('MYSQLDATABASE'))

# Initialize Flask app
Server = Flask(__name__)

# Enable CORS *after* defining Flask app
CORS(Server)

def get_db_connection():
    """ Establishes and returns a MySQL database connection. """
    try:
        print("🔹 Attempting to connect to MySQL...")
        conn = mysql.connector.connect(
            host=os.getenv('MYSQLHOST'),
            port=int(os.getenv('MYSQLPORT')),
            user=os.getenv('MYSQLUSER'),
            password=os.getenv('MYSQLPASSWORD'),
            database=os.getenv('MYSQLDATABASE')
        )
        print("✅ MySQL connection successful!")
        return conn
    except mysql.connector.Error as e:
        print("❌ MySQL Connection Error:", e)
        return None

# Manual MySQL connection test before running Flask
test_conn = get_db_connection()
if test_conn:
    test_conn.close()
else:
    print("❌ MySQL connection test failed! Check your database credentials.")
    exit(1)  # Stop the script if MySQL connection fails

@Server.route('/register', methods=['POST'])
def register():
    """ Handles user registration with basic validation. """
    print("🔹 Received a registration request")  # Debugging log

    try:
        data = request.get_json()
        print("📥 Received Data:", data)  # Debugging log

        if not data or 'username' not in data or 'password' not in data:
            print("❌ Invalid input data!")
            return jsonify(success=False, message="Invalid input"), 400

        conn = get_db_connection()
        if not conn:
            print("❌ Database connection failed!")
            return jsonify(success=False, message="Database connection failed"), 500

        cursor = conn.cursor()

        # Check if the username already exists
        cursor.execute("SELECT * FROM users WHERE username=%s", (data['username'],))
        existing_user = cursor.fetchone()

        if existing_user:
            print("❌ Username already exists!")
            return jsonify(success=False, message="Username already exists"), 400

        # Insert the new user
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (data['username'], data['password']))
        conn.commit()

        print("✅ Registration successful!")
        return jsonify(success=True, message="User registered successfully")

    except mysql.connector.Error as e:
        print("❌ MySQL Error:", e)
        return jsonify(success=False, message=f"Database error: {str(e)}"), 500
    except Exception as e:
        print("❌ General Error:", e)
        return jsonify(success=False, message=f"Unexpected error: {str(e)}"), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    Server.run(host='0.0.0.0', port=8000, debug=True)  # Debug mode enabled

@Server.route('/login', methods=['POST'])
def login():
    """Handles user login."""
    print("🔹 Received a login request")  # Debugging log

    try:
        data = request.get_json()
        print("📥 Received Data:", data)  # Debugging log

        if not data or 'username' not in data or 'password' not in data:
            print("❌ Invalid input data!")
            return jsonify(success=False, message="Invalid input"), 400

        conn = get_db_connection()
        if not conn:
            print("❌ Database connection failed!")
            return jsonify(success=False, message="Database connection failed"), 500

        cursor = conn.cursor()

        # Check if the username exists
        cursor.execute("SELECT * FROM users WHERE username=%s", (data['username'],))
        user = cursor.fetchone()

        if not user:
            print("❌ Username not found!")
            return jsonify(success=False, message="Invalid username or password"), 401

        # Check if the password matches (⚠️ In production, use hashed passwords!)
        stored_password = user[2]  # Assuming password is the 3rd column in DB
        if stored_password != data['password']:
            print("❌ Incorrect password!")
            return jsonify(success=False, message="Invalid username or password"), 401

        print("✅ Login successful!")
        return jsonify(success=True, message="Login successful")

    except mysql.connector.Error as e:
        print("❌ MySQL Error:", e)
        return jsonify(success=False, message=f"Database error: {str(e)}"), 500
    except Exception as e:
        print("❌ General Error:", e)
        return jsonify(success=False, message=f"Unexpected error: {str(e)}"), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'conn' in locals():
            conn.close()
