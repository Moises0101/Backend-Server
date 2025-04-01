from flask import Flask, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv
from flask_cors import CORS  # Import CORS to handle cross-origin requests

print("🔹 MySQL Connector is installed and working!")

# Load environment variables from the .env file
if not load_dotenv():
    print("⚠️ Warning: .env file not found or failed to load!")

# Debugging: Print loaded environment variables
print("🔹 ENV VARIABLES CHECK")
print("🔹 MYSQL_HOST:", os.getenv('MYSQLHOST'))  # Display the MySQL host
print("🔹 MYSQL_PORT:", os.getenv('MYSQLPORT'))  # Display the MySQL port
print("🔹 MYSQL_USER:", os.getenv('MYSQLUSER'))  # Display the MySQL username
print("🔹 MYSQL_PASSWORD:", "********")  # Masked for security (don't print passwords)
print("🔹 MYSQL_DATABASE:", os.getenv('MYSQLDATABASE'))  # Display the MySQL database name

# Initialize Flask app
Server = Flask(__name__)

# Enable CORS after defining the Flask app to allow cross-origin requests
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
        print("❌ MySQL Connection Error:", e)  # If connection fails, print error
        return None

# Manual MySQL connection test before running Flask
test_conn = get_db_connection()
if test_conn:
    test_conn.close()  # Close the test connection if successful
else:
    print("❌ MySQL connection test failed! Check your database credentials.")
    exit(1)  # Stop the script if MySQL connection fails

# Route for user registration
@Server.route('/register', methods=['POST'])
def register():
    """ Handles user registration with basic validation. """
    print("🔹 Received a registration request")  # Debugging log

    try:
        data = request.get_json()  # Parse JSON data from the request
        print("📥 Received Data:", data)  # Debugging log

        if not data or 'username' not in data or 'password' not in data:
            print("❌ Invalid input data!")  # If username or password are missing
            return jsonify(success=False, message="Invalid input"), 400

        conn = get_db_connection()  # Establish DB connection
        if not conn:
            print("❌ Database connection failed!")  # If DB connection fails
            return jsonify(success=False, message="Database connection failed"), 500

        cursor = conn.cursor()

        # Check if the username already exists in the database
        cursor.execute("SELECT * FROM users WHERE username=%s", (data['username'],))
        existing_user = cursor.fetchone()

        if existing_user:  # If user exists, return error
            print("❌ Username already exists!")
            return jsonify(success=False, message="Username already exists"), 400

        # Insert the new user into the database
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)", (data['username'], data['password']))
        conn.commit()  # Commit the transaction

        print("✅ Registration successful!")  # Success log
        return jsonify(success=True, message="User registered successfully")

    except mysql.connector.Error as e:
        print("❌ MySQL Error:", e)  # If MySQL error occurs
        return jsonify(success=False, message=f"Database error: {str(e)}"), 500
    except Exception as e:
        print("❌ General Error:", e)  # Catch other errors
        return jsonify(success=False, message=f"Unexpected error: {str(e)}"), 500
    finally:
        if 'cursor' in locals():
            cursor.close()  # Close the cursor if it exists
        if 'conn' in locals():
            conn.close()  # Close the connection if it exists

# Route for user login
@Server.route('/login', methods=['POST'])
def login():
    """ Handles user login. """
    print("🔹 Received a login request")  # Debugging log

    try:
        data = request.get_json()  # Parse JSON data from the request
        print("📥 Received Data:", data)  # Debugging log

        if not data or 'username' not in data or 'password' not in data:
            print("❌ Invalid input data!")  # If username or password are missing
            return jsonify(success=False, message="Invalid input"), 400

        conn = get_db_connection()  # Establish DB connection
        if not conn:
            print("❌ Database connection failed!")  # If DB connection fails
            return jsonify(success=False, message="Database connection failed"), 500

        cursor = conn.cursor()

        # Check if the username exists in the database
        cursor.execute("SELECT * FROM users WHERE username=%s", (data['username'],))
        user = cursor.fetchone()

        if not user:  # If user doesn't exist, return error
            print("❌ Username not found!")
            return jsonify(success=False, message="Invalid username or password"), 401

        # Check if the password matches (⚠️ In production, use hashed passwords for security!)
        stored_password = user[2]  # Assuming password is stored as the 3rd column in DB
        if stored_password != data['password']:  # If passwords don't match, return error
            print("❌ Incorrect password!")
            return jsonify(success=False, message="Invalid username or password"), 401

        print("✅ Login successful!")  # Success log
        return jsonify(success=True, message="Login successful")

    except mysql.connector.Error as e:
        print("❌ MySQL Error:", e)  # If MySQL error occurs
        return jsonify(success=False, message=f"Database error: {str(e)}"), 500
    except Exception as e:
        print("❌ General Error:", e)  # Catch other errors
        return jsonify(success=False, message=f"Unexpected error: {str(e)}"), 500
    finally:
        if 'cursor' in locals():
            cursor.close()  # Close the cursor if it exists
        if 'conn' in locals():
            conn.close()  # Close the connection if it exists

# Run the Flask app
if __name__ == "__main__":
    Server.run(host='0.0.0.0', port=8000, debug=True)  # Start the Flask app on all IPs, port 8000, with debug mode enabled
