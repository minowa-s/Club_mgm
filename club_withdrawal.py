from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

club_withdrawal_bp =  Blueprint('club_withdrawal', __name__, url_prefix='/club_withdrawal')

def get_connection():
    connection = psycopg2.connect(
        host = 'ec2-44-213-151-75.compute-1.amazonaws.com',
        port = 5432,
        user = 'uzfoqqwpjlxmdm',
        database = 'd6nhl8cv0snufq',
        password = '3d0d14a3a20adcd96401c248ed43ca6df9072fac916521987ebe79a2c711cbd4'
    )
    return connection

#学生サークル脱退機能
@club_withdrawal_bp.route('/club_withdrawal', methods=['POST'])
def club_withdrawal():
    club_name = request.args.get('club_name')
    return render_template('withdrawal/withdrawal_club_conf.html', club_name = club_name)
    
@club_withdrawal_bp.route('/club_withdrawal_res', methods=['POST'])
def club_withdrawal_res():
    club_name = request.args.get('club_name')
    mail = session.get('mail')
    club_id = get_club_id(club_name)
    student_id = get_student_id(mail)
    
    delete_student_club(student_id, club_id)
    return render_template('withdrawal/withdrawal_club_res.html')

#サークルリーダー脱退機能
@club_withdrawal_bp.route('/club_withdrawal_lea', methods=['POST'])
def club_withdrawal_lea():
    club_name = request.args.get('club_name')
    return render_template('withdrawal/withdrawal_club_conf_lea.html', club_name = club_name)
    
@club_withdrawal_bp.route('/club_withdrawal_res_lea', methods=['POST'])
def club_withdrawal_res_lea():
    club_name = request.args.get('club_name')
    mail = session.get('mail')
    club_id = get_club_id(club_name)
    student_id = get_student_id(mail)
    
    delete_student_club(student_id, club_id)
    return render_template('withdrawal/withdrawal_club_res_lea.html')

#学生会サークル脱退機能
@club_withdrawal_bp.route('/club_withdrawal_cou', methods=['POST'])
def club_withdrawal_cou():
    club_name = request.args.get('club_name')
    return render_template('withdrawal/withdrawal_club_conf_cou.html', club_name = club_name)
    
@club_withdrawal_bp.route('/club_withdrawal_res_cou', methods=['POST'])
def club_withdrawal_res_cou():
    club_name = request.args.get('club_name')
    mail = session.get('mail')
    club_id = get_club_id(club_name)
    student_id = get_student_id(mail)
    
    delete_student_club(student_id, club_id)
    return render_template('withdrawal/withdrawal_club_res_cou.html')

def get_student_id(mail):
    sql = "SELECT student_id FROM student WHERE mail = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (mail,))
    studnet_id = cursor.fetchone()
    cursor.close()
    connection.close()
    return studnet_id[0] if studnet_id else None

# クラブidを取得するメソッド    
def get_club_id(club_name):
    sql = "SELECT club_id FROM club WHERE name = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_name,))
    club_id = cursor.fetchone()
    cursor.close()
    connection.close()
    return club_id[0] if club_id else None

#student_clubテーブルから情報を削除するメソッド
def delete_student_club(student_id, club_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "DELETE FROM student_club WHERE student_id = %s AND club_id =%s "
    cursor.execute(sql, (student_id,club_id))
    connection.commit()
    cursor.close()
    connection.close()