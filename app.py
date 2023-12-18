from flask import Flask,Blueprint,  render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os, psycopg2, string, random, hashlib

app = Flask(__name__)
app.secret_key = 'secret_key'

from account import account_bp
app.register_blueprint(account_bp)
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

from app_req import club_req
app.register_blueprint(club_req)
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection
    
from app_deta import club_deta
app.register_blueprint(club_deta)
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/top')
def top():
    return render_template('top.html')

@app.route('/page_b')
def page_b():
    return render_template('page_b.html')
        
@app.route('/page_c')
def page_c():
    return render_template('page_c.html')

@app.route('/sample2')
def sample():
    return render_template('sample2.html')

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    
    