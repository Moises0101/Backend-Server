from flask import Flask, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv
import mysql.connector
print("MySQL Connector is installed and working!")
# Load environment variables from the .env file
load_dotenv()

Server = Flask(__name__)


def get_db_connection():
    try:
        print("🔹 ENV VARIABLES CHECK")  # Debugging
        print("🔹 MYSQL_HOST:", os.getenv('MYSQL_HOST'))
        print("🔹 MYSQL_PORT:", os.getenv('MYSQL_PORT'))
        print("🔹 MYSQL_USER:", os.getenv('MYSQL_USER'))

        conn = mysql.connector.connect(
            host=os.getenv('MYSQL_HOST', 'mysql.railway.internal'),
            port=int(os.getenv('MYSQL_PORT', 3306)),  # Default to 3307 if not set
            user=os.getenv('MYSQL_USER', 'root'),
            password=os.getenv('MYSQL_PASSWORD', 'Programmer01!'),
            database=os.getenv('MYSQL_DATABASE', 'railway')
        )
        print("✅ MySQL connection successful!")
        return conn
    except mysql.connector.Error as e:
        print("❌ MySQL Connection Error:", e)
        return None


@Server.route('/register', methods=['POST'])
def register():
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
    Server.run(host='0.0.0.0', port=8000)
