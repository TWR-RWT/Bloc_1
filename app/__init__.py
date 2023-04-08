#! C:\Users\tgp\AppData\Local\Programs\Python\Python310\python.exe
import os
import psycopg2
from dotenv import load_dotenv
from psycopg2 import connect
from psycopg2.pool import SimpleConnectionPool
from contextlib import contextmanager
import os
from flask import Flask, render_template, session, request, redirect, url_for, flash
from flask import jsonify
from flask import session
import jwt
from functools import wraps
from jinja2 import Template
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta


app = Flask(__name__)

app.secret_key = "very-secret-key"

# Charger les variables d'environnement depuis le fichier .env
load_dotenv()

# Variables d'environnement pour la connexion à la base de données
db_host = os.getenv("POSTGRES_DB_HOST")
db_port = os.getenv("POSTGRES_DB_PORT")
db_name = os.getenv("POSTGRES_DB_NAME")
db_user = os.getenv("POSTGRES_DB_USER")
db_password = os.getenv("POSTGRES_DB_PASS")


# initialise la pool de connexions
pool = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    host=db_host,
    port=db_port,
    dbname=db_name,
    user=db_user,
    password=db_password,
    cursor_factory=None,
)

# contextmanager pour simplifier la gestion de la connexion
@contextmanager
def get_db():
    conn = pool.getconn()
    try:
        yield conn
    finally:
        pool.putconn(conn)

# decorateur token verification
def token_required_auth(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = session.get('token')
        if not token:
            return jsonify({'Alert!': 'Token is missing!'}), 401
        #try:
        data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'])
        #except:
        #    return jsonify({'Message': 'Invalid token'}), 403
        return func(*args, **kwargs)
    return decorated

@app.route("/")
def index():
    if not session.get('logged_in'):
        return render_template('/authentification/login.html')
    else:
        return render_template('/main/welcome.html')

from app import authentification
from app import main


# exemple d'utilisation de la connexion
"""
with get_db() as conn:
    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM client")
        rows = cursor.fetchall()
        print(rows)
"""