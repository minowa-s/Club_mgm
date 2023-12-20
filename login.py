from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

login_bp = Blueprint('login', __name__, url_prefix='/login')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

def get_salt():
    charset = string.ascii_letters + string.digits
    
    salt = ''.join(random.choices(charset, k=30))
    return salt

def get_hash(password, salt):
    b_pw = bytes(password, "utf-8")
    b_salt = bytes(salt, "utf-8")
    hashed_password = hashlib.pbkdf2_hmac("sha256", b_pw, b_salt, 1000).hex()
    return hashed_password


#生徒ログイン
def login_student(mail, password):
    sql = 'SELECT hashed_password, salt FROM student WHERE mail = %s'
    flg = False
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (mail,))
        user = cursor.fetchone()
        
        if user !=  None :
            salt = user[1]
            
            hashed_password = get_hash(password, salt)
            
            if hashed_password == user[0] :
                flg = True
    
    except psycopg2.DatabaseError :
        flg = False
    
    finally :
        cursor.close()
        connection.close()
    
    return flg

#教員ログイン
def login_teacher(mail, password):
    sql = 'SELECT hashed_password, salt FROM teacher WHERE mail = %s'
    flg = False
    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(sql, (mail,))
        user = cursor.fetchone()
        
        if user !=  None :
            salt = user[1]
            
            hashed_password = get_hash(password, salt)
            
            if hashed_password == user[0] :
                flg = True
    
    except psycopg2.DatabaseError :
        flg = False
    
    finally :
        cursor.close()
        connection.close()
    
    return flg