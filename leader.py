from flask import Blueprint, redirect, render_template, request, session, url_for
import hashlib, string, random, psycopg2, db, os, bcrypt, datetime, smtplib, club
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

leader_bp = Blueprint('leader', __name__, url_prefix='/leader')

#DB接続
def get_connection():
    connection = psycopg2.connect(
        host = 'ec2-54-205-67-130.compute-1.amazonaws.com',
        port = 5432,
        user = 'hpmpphajmsgupf',
        database = 'def063tgglhgba',
        password = 'e8d1d1bce580c7529b0a61b91773c3b407b77ac49ba0a91ac20388370e7b3c47'
    )
    return connection

@leader_bp.route()
def request_list():
    mail = session.get('mail')
    id = db.get_id(mail)
    club_id = db.get_club_id(id)
    request_list = get_request(club_id)
    return render_template('leader/request_list.html', request_list=request_list)

def get_request():
    sql = "SELECT * FROM student_club WHERE allow = 0, club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    list = cursor.fetchall()
    cursor.close()
    connection.close()
    return list