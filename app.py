from flask import Flask,Blueprint,  render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import os, psycopg2, string, random, hashlib

app = Flask(__name__)
app.secret_key = 'secret_key'

#ブループリントimport-----------------
from account import account_bp       
app.register_blueprint(account_bp)
from club import club_bp
app.register_blueprint(club_bp)
from club2 import club_bp2
app.register_blueprint(club_bp2)
from app_data import app_data_bp
app.register_blueprint(app_data_bp)
#------------------------------------

def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection
    
@app.route('/')
def index():
    return render_template('top_teacher.html')

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    
    