import mysql.connector
import re

pattern = r'[!@#$%^&*(),.?\":{}|<>]'

conn = mysql.connector.connect(
host = "localhost",
user = "root",
password = "",
database = "lenrich"
)
cursor = conn.cursor()

def registration():
    print("Registration")
    username = input("Enter username: ")
    password = input("Enter Password: ")
    cursor.execute("SELEECT * FROM tbluser WHERE username = %s", (username,))
    existing_user = cursor.fetchone()
    if len(username) < 5 or len(password) < 8 or len(username) > 16 or len(password) > 16:
        print("Minimum characters for username is 5 while the Minimum of password is 8\nMaximum of username and passsword is 16")
    elif re.search(r'\s', username) or  re.search(r'\s', password) or re.search(r'\d', username) or re.search(r'\d', password):
        print("Numbers, Spaces and special characters cannot be included.")
    else:
        if existing_user:
            print("Username already exists! please choose a different one.")
            return
        query = "INSERT INTO tbluser (username, password) VALUES(%s,%s)"
        cursor.execute(query, (username,password))
        conn.commit()
        print("Registration Successful")

def login():
    username = input("Enter username: ")
    password = input("Enter password: ")

    query = "SELECT * FROM tbluser WHERE username = %s AND password = %s"
    result = cursor.fetchone()
    if result:
        print("Logged in Successfully!\n Welcome Summoner.")
    else:
        print("Invalid username or password. Please Try again.")

while True:
    reglog = int(input("[1]Register\n[2]Login\n[3]Exit\n:"))
    match reglog:
        case 1:
            registration()
        case 2:
            login()
        case _:
            break