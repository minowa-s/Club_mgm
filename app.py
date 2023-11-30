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
    
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/page_a')
def page_a():
    return render_template('page_a.html')

@app.route('/page_b')
def page_b():
    return render_template('page_b.html')
        
@app.route('/page_c')
def page_c():
    return render_template('page_c.html')

if __name__ == '__main__':
    app.run(debug=True)
    
    
    
    
    