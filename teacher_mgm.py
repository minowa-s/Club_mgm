from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

teacher_mgm_bp = Blueprint('teacher_mgm', __name__, url_prefix='/teacher_mgm')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

@teacher_mgm_bp.route('/teacher_display')
def teacher_display():
    tea_list = get_teacher()
    return render_template('teacher_disp.html' ,teacher = tea_list)

def get_teacher():
    connection = get_connection()
    cursor = connection.cursor()
    
    sql = "SELECT * FROM teacher "
    
    cursor.execute(sql,)
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows

@teacher_mgm_bp.route('/teacher_delete', methods=['POST'])
def teacher_delete():
    name = request.args.get('name')
    mail = request.args.get('mail')
    return render_template('delete_teacher_conf.html', mail = mail, name = name)

@teacher_mgm_bp.route('/teacher_delete_res' , methods=['POST'])
def teacher_delete_res():
    mail = request.args.get('mail')
    delete_teacher(mail)
    return render_template('delete_teacher_res.html')

def delete_teacher(mail):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "DELETE FROM teacher WHERE mail = %s"
    cursor.execute(sql, (mail,))
    connection.commit()
    cursor.close()
    connection.close()