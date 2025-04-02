from flask import Flask, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import CORS  # Enable Cross-Origin Resource Sharing (CORS)

print("🔹 MySQL Connector is installed and working!")

# Load environment variables from the .env file
if not load_dotenv():
    print("⚠️ Warning: .env file not found or failed to load!")

# Debugging: Print essential environment variables
print("🔹 ENV VARIABLES CHECK")
print("🔹 MYSQL_HOST:", os.getenv('MYSQLHOST'))
print("🔹 MYSQL_PORT:", os.getenv('MYSQLPORT'))
print("🔹 MYSQL_USER:", os.getenv('MYSQLUSER'))
print("🔹 MYSQL_PASSWORD:", "********")  # Masked for security
print("🔹 MYSQL_DATABASE:", os.getenv('MYSQLDATABASE'))

# Initialize Flask app
Server = Flask(__name__)

# Enable CORS to allow cross-origin requests
CORS(Server)

# Function to establish a MySQL database connection
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

# Test the database connection before starting the server
test_conn = get_db_connection()
if test_conn:
    test_conn.close()
else:
    print("❌ MySQL connection test failed! Check your database credentials.")
    exit(1)

# Route for user registration
@Server.route('/register', methods=['POST'])
def register():
    """ Handles user registration by storing username and password. """
    print("🔹 Received a registration request")

    try:
        data = request.get_json()  # Parse incoming JSON request
        print("📥 Received Data:", data)

        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            print("❌ Invalid input data!")
            return jsonify(success=False, message="Invalid input"), 400

        conn = get_db_connection()
        if not conn:
            print("❌ Database connection failed!")
            return jsonify(success=False, message="Database connection failed"), 500

        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username=%s", (data['username'],))
        existing_user = cursor.fetchone()

        if existing_user:
            print("❌ Username already exists!")
            return jsonify(success=False, message="Username already exists"), 400

        # Insert new user into the database (⚠️ Hash passwords in production!)
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

# Route for user login
@Server.route('/login', methods=['POST'])
def login():
    """ Handles user login by verifying username and password. """
    print("🔹 Received a login request")

    try:
        data = request.get_json()
        print("📥 Received Data:", data)

        # Validate required fields
        if not data or 'username' not in data or 'password' not in data:
            print("❌ Invalid input data!")
            return jsonify(success=False, message="Invalid input"), 400

        conn = get_db_connection()
        if not conn:
            print("❌ Database connection failed!")
            return jsonify(success=False, message="Database connection failed"), 500

        cursor = conn.cursor()

        # Retrieve user from database
        cursor.execute("SELECT * FROM users WHERE username=%s", (data['username'],))
        user = cursor.fetchone()

        if not user:
            print("❌ Username not found!")
            return jsonify(success=False, message="Invalid username or password"), 401

        # Check if password matches (⚠️ Use hashed passwords in production!)
        stored_password = user[2]  # Assuming password is stored in the 3rd column
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

# Start the Flask app
if __name__ == "__main__":
    Server.run(host='0.0.0.0', port=8000, debug=True)  # Run server on all IPs, port 8000
