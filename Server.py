from flask import Flask, request, jsonify
import mysql.connector
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

Server = Flask(__name__)


def get_db_connection():
    # Debugging: Print environment variables before connecting
    print("🔹 MYSQL_HOST:", os.getenv('MYSQL_HOST'))
    print("🔹 MYSQL_PORT:", os.getenv('MYSQL_PORT'))
    print("🔹 MYSQL_USER:", os.getenv('MYSQL_USER'))

    return mysql.connector.connect(
        host=os.getenv('MYSQL_HOST', 'localhost'),
        port=int(os.getenv('MYSQL_PORT', 3307)),  # Ensure correct port
        user=os.getenv('MYSQL_USER', 'root'),
        password=os.getenv('MYSQL_PASSWORD', 'Programmer01!'),
        database=os.getenv('MYSQL_DATABASE', 'login_system')
    )


@Server.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()  # Get the data sent by the client

        if not data or 'username' not in data or 'password' not in data:
            return jsonify(success=False, message="Invalid input"), 400  # Invalid input check

        conn = get_db_connection()
        cursor = conn.cursor()

        # Check if username already exists
        cursor.execute("SELECT * FROM users WHERE username=%s", (data['username'],))
        existing_user = cursor.fetchone()
        if existing_user:
            return jsonify(success=False, message="Username already exists"), 400

        # Insert the user into the database
        cursor.execute("INSERT INTO users (username, password) VALUES (%s, %s)",
                       (data['username'], data['password']))
        conn.commit()  # Commit the changes to the database
        return jsonify(success=True, message="User registered successfully")

    except mysql.connector.Error as e:
        print("❌ MySQL Error:", e)
        return jsonify(success=False, message=f"Database error: {str(e)}"), 500
    except Exception as e:
        print("❌ General Error:", e)
        return jsonify(success=False, message=f"Unexpected error: {str(e)}"), 500
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    Server.run(host='0.0.0.0', port=8000)
