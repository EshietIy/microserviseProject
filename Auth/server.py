import os
import jwt
import datetime
from flask import Flask, request
from flask_mysqldb import MySQL

server = Flask(__name__)
mysql = MySQL(server)

# MySQL configurations
server.config["MYSQL_HOST"] = os.getenv("MYSQL_HOST")
server.config["MYSQL_USER"] = os.getenv("MYSQL_USER")
server.config["MYSQL_PASSWORD"] = os.getenv("MYSQL_PASSWORD")
server.config["MYSQL_DB"] = os.getenv("MYSQL_DB")
server.config["MYSQL_PORT"] = os.getenv("MYSQL_PORT")

@server.route("/login", methods=["POST"])
def login():
    auth = request.authorization
    if not auth:
        return "Missing credentials", 401

    #check db for userr credentials
    cur = mysql.connection.cursor()
    res = cur.execute("SELECT * FROM users WHERE username=%s", (auth.username,))

    if res > 0:
        user = cur.fetchone()
        email = user[0]
        password = user[1]

        if auth.password != password or auth.username != email:
            return "Invalid credentials", 401
        else:
            token = create_token(email, os.getenv("SECRET_KEY"), True)
    else:
        return "User not found", 404
    
    return {"token": token}, 200



# verify token
@server.route("/validate", methods=["POST"])
def validate():
    token = request.headers.get("Authorization")
    if not token:
        return "Credential is missing", 401
    encoded_token = token.split(" ")[1]
    try:
        payload = jwt.decode(encoded_token, os.getenv("SECRET_KEY"), algorithms="HS256")
    except:
        return "Invalid token", 403
    return payload, 200


def create_token(email, secret_key, is_admin):
    payload = {
        "email": email,
        "admin": is_admin,
        "iat": datetime.datetime.utcnow(),
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=1)
    }
    return jwt.encode(payload, secret_key, algorithm="HS256")

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=5000)   