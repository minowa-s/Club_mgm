from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

account_search_bp = Blueprint('account_search', __name__, url_prefix='/account_search')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

#学生アカウント検索
@account_search_bp.route("/student_search")
def student_search():
    return render_template("student_search.html")

@account_search_bp.route("/student_search_res",methods=["POST"])
def student_search_res():
    name = request.form.get("name")
    
    if name == "高度情報工学科":
        department_num = 1
        stu_list = search_department(department_num)
    elif name == "総合システム工学科":
        department_num = 2
        stu_list = search_department(department_num)
    elif name == "情報システム科":
        department_num = 3
        stu_list = search_department(department_num)
    elif name == "情報ビジネス科":
        department_num = 4
        stu_list = search_department(department_num)
    elif name == "総合デザイン科":
        department_num = 5
        stu_list = search_department(department_num)
    elif name == "グラフィックデザインコース":
        department_num = 6
        stu_list = search_department(department_num)
    elif name == "アニメ・マンガコース":
        department_num = 7
        stu_list = search_department(department_num)
    elif name == "CGクリエイトコース":
        department_num = 8
        stu_list = search_department(department_num)
    elif name == "建築インテリアコース":
        department_num = 9
        stu_list = search_department(department_num)
    else:
        stu_list = student_search(name)
        
    return render_template("student_search_result.html", students = stu_list )
        
#学生アカウント検索
def student_search(name):
    connection = get_connection()
    cursor = connection.cursor()
    
    sql = "SELECT * FROM student WHERE name LIKE %s"
    name2 = "%" + name + "%"
    
    cursor.execute(sql,(name2,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows

def search_department(department_num):
    connection = get_connection()
    cursor = connection.cursor()
    
    sql = "SELECT * FROM student WHERE department_id = %s"
    
    cursor.execute(sql,(department_num,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows

def count_club(name):
    connection = get_connection()
    cursor = connection.cursor()
    sql = "SELECT COUNT (club_id) FROM student_club WHERE name LIKE %s"
    name2 = "%" + name + "%"
    cursor.execute(sql,(name2,))
    rows = cursor.fetchall()
    cursor.close()
    connection.close()
    return rows