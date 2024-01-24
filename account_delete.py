from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

account_delete_bp = Blueprint('account_delete', __name__, url_prefix='/account_delete')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

@account_delete_bp.route('/account_delete', methods = ["POST"])
def account_delete():
    #セッションからメールアドレスを取得する
    #mail = session.get("student_mail")
    mail = request.args.get("mail")
    
    #学科を取得する
    department_num = get_department_num(mail)
    print(department_num)
    department = ' '
    if department_num == 1:
        department = "高度情報工学科"
        
    elif department_num == 2:
        department == "総合システム工学科"
        
    elif department_num == 3:
        department == "情報システム科"
        
    elif department_num == 4:
        department == "情報ビジネス科"
        
    elif department_num == 5:
        department == "総合デザイン科"
        
    elif department_num == 6:
        department == "グラフィックデザインコース"
        
    elif department_num == 7:
        department == "アニメマンガコース"
        
    elif department_num == 8:
        department == "CGクリエイトコース"
        
    elif department_num == 9:
        department == "建築インテリアコース"
        
    else:
        department == "null"
    
    print(department)
    #削除したい学生のidを取得する
    student_id = get_student_id(mail)
    
    #削除したい学生の名前を取得する
    name = get_student_name(student_id)
    print(name)
    entrance_year = request.args.get("entrance_year")
    
    return render_template("account_delete_conf.html" ,mail = mail ,department = department, name = name, entrance_year = entrance_year )

def get_department_num(mail):
    connection = get_connection()
    cursor = connection.cursor()
    
    sql = "SELECT department_id FROM student WHERE mail = %s"
    
    cursor.execute(sql,(mail,))
    department_num = cursor.fetchone()
    cursor.close()
    connection.close()
    return department_num[0] if department_num else None

def get_student_id(mail):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT student_id FROM student WHERE mail = %s"
    cursor.execute(sql, (mail,))
    student_id = cursor.fetchone()
    cursor.close()
    connection.close()
    return student_id[0] if student_id else None

def get_student_name(student_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT name FROM student WHERE student_id = %s"
    cursor.execute(sql, (student_id,))
    name = cursor.fetchone()
    cursor.close()
    connection.close()
    return name[0] if name else None
    
@account_delete_bp.route('/account_delete_conf' , methods=['POST'])
def account_delete_conf():
    mail = request.args.get("mail")
    
    student_id = get_student_id(mail)
    #studentテーブルにあるデータを削除
    delete_student(student_id)
    
    #student_clubテーブルにあるデータを削除
    delete_student_club(student_id)
    print(student_id)
    return render_template("account_delete_res.html")
    
def delete_student(student_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "DELETE FROM student WHERE student_id = %s"
    cursor.execute(sql, (student_id,))
    connection.commit()
    cursor.close()
    connection.close()
    
def delete_student_club(student_id):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "DELETE FROM student WHERE student_id = %s"
    cursor.execute(sql, (student_id,))
    connection.commit()
    cursor.close()
    connection.close()