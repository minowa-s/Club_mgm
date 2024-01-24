from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

club_delete_tea_bp = Blueprint('club_delete_tea', __name__, url_prefix='/club_delete_tea')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

@club_delete_tea_bp.route('/club_delete_tea', methods = ['POST'])
def club_delete_tea():
    name = request.args.get('name')
    return render_template('delete_club_tea_conf.html', name = name)

@club_delete_tea_bp.route('/club_delete_tea_conf', methods = ['POST'])
def club_delete_tea_conf():
    name = request.args.get('name')
    club_id = get_club_id(name)
    delete_club(club_id)
    delete_student_club(club_id)
    return render_template('delete_club_tea_res.html')

def get_club_id(name):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT club_id FROM club WHERE name = %s" 
    cursor.execute(sql,(name,))
    club_id = cursor.fetchone()
    cursor.close()
    connection.close()
    return club_id[0] if club_id else None

def delete_club(club_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "DELETE FROM club WHERE club_id = %s" 
    cursor.execute(sql,(club_id,))
    connection.commit()
    cursor.close()
    connection.close()
    
def delete_student_club(club_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "DELETE FROM student_club WHERE club_id = %s" 
    cursor.execute(sql,(club_id,))
    connection.commit()
    cursor.close()
    connection.close()
    
    