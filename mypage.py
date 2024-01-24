from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

mypage_bp = Blueprint('mypage_bp', __name__, url_prefix='/mypage_bp')

#DB接続
def get_connection():

    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

#マイページ機能
@mypage_bp.route('/')
def mypage():
    mail = session.get('mail')
    name = get_name(mail)
    entrance_year = get_entrance_year(mail)
    department_id = get_department_id(mail)
    department = get_department(department_id)
    student_id = get_student_id(mail)
    club_id_list = get_club_id(student_id)
    club_name_list = []
    for n in club_id_list:
        club_name_list.append(get_club_name(n)) 
    return render_template('mypage/mypage.html', mail = mail, name = name, entrance_year = entrance_year, department = department, club_name_list = club_name_list)
    
#サークルリーダー
#マイページ機能
@mypage_bp.route('/mypage_lea')
def mypage_lea():

    mail = session.get('mail')

    name = get_name(mail)
    entrance_year = get_entrance_year(mail)
    department_id = get_department_id(mail)
    department = get_department(department_id)
    student_id = get_student_id(mail)
    club_id_list = get_club_id(student_id)
    club_name_list = []
    for n in club_id_list:
        club_name_list.append(get_club_name(n)) 
    print(club_name_list)
    return render_template('mypage/mypage_lea.html', mail = mail, name = name, entrance_year = entrance_year, department = department, club_name_list = club_name_list)

#学生会マイページ機能
@mypage_bp.route('/mypage_cou')
def mypage_cou():
    
    #セッションからメールアドレスを取得
    # mail = request.session.get['mail']
    mail = request.form.get("mail")
    session['mail'] = mail
    
    #下のget_nameをメールアドレスを引数に実行
    name = get_name(mail)
    
    #下のget_entrance_yearをメールアドレスを引数に実行
    entrance_year = get_entrance_year(mail)
    
    #下のget_department_idをメールアドレスを引数に実行
    department_id = get_department_id(mail)
    
    #下のget_departmentをdepartment_idを引数に実行
    department = get_department(department_id)
    
    print(name)
    
    # 下のget_student_idをメールアドレスを引数に実行
    student_id = get_student_id(mail)
    
    #下のget_club_idをstudent_idを引数に実行
    club_id_list = get_club_id(student_id)
    print(club_id_list)
    
    #下のget_club_nameをclub_idを引数に実行
    club_name_list = []
    
    for n in club_id_list:
        club_name_list.append(get_club_name(n)) 
        
    print(club_name_list)
        
    return render_template('mypage/mypage_cou.html', mail = mail, name = name, entrance_year = entrance_year, department = department, club_name_list = club_name_list)

#名前を取得するメソッド    
def get_name(mail):
    sql = "SELECT name FROM student WHERE mail = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (mail,))
    name = cursor.fetchone()
    cursor.close()
    connection.close()
    return name[0] if name else None
    
#入学年度を取得するメソッド
def get_entrance_year(mail):
    sql = "SELECT entrance_year FROM student WHERE mail = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (mail,))
    entrance_year = cursor.fetchone()   
    cursor.close()
    connection.close()
    return entrance_year[0] if entrance_year else None

#学科idを取得するメソッド
def get_department_id(mail):
    sql = "SELECT department_id FROM student WHERE mail = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (mail,))
    department_id = cursor.fetchone()   
    cursor.close()
    connection.close()
    return department_id

#学科を取得するメソッド
def get_department(department_id):
    sql = "SELECT name FROM department WHERE department_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (department_id,))
    department = cursor.fetchone()
    cursor.close()
    connection.close()
    return department[0] if department else None
    
#学生idを取得するメソッド
def get_student_id(mail):
    sql = "SELECT student_id FROM student WHERE mail = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (mail,))
    studnet_id = cursor.fetchone()
    cursor.close()
    connection.close()
    return studnet_id

# クラブidを取得するメソッド    
def get_club_id(student_id):
    sql = "SELECT club_id FROM student_club WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql,(student_id,))
    club_id_list = []
    for row in cursor.fetchall():
        club_id_list.append((row[0])) #row[0]=student_id,
    cursor.close()
    connection.close()
    return club_id_list

#クラブ名を取得するメソッド
def get_club_name(club_id_list):
    sql = "SELECT name FROM club WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id_list,))
    club_name = cursor.fetchone()
    cursor.close()
    connection.close()
    return club_name
    
@mypage_bp.route('/mypage_tea')
def mypage_tea():
    mail = session.get('mail')
    name = get_tea_name(mail)
    return render_template('mypage/mypage_tea.html', mail = mail, name = name)

def get_tea_name(mail):
    sql = "SELECT name FROM teacher WHERE mail = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (mail,))
    name = cursor.fetchone()
    cursor.close()
    connection.close()
    return name[0] if name else None