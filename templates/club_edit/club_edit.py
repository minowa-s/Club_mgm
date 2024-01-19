from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

club_edit_bp = Blueprint('club_edit', __name__, url_prefix='/club_edit')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

#サークルリーダーの変更申請処理
@club_edit_bp.route('/club_edit_start', methods=['POST'])
def club_edit_start():
    #ログインでidをセッションに保存してあるので本番ではsession.getにする。form.getのは動作確認用
    #student_id = session.get("student_id")
    student_id = request.form.get("student_id")
    club_id = get_club_id(student_id)
    session["club_id"] = club_id
    return render_template('club_edit_input.html')
   
# クラブidを取得するメソッド  
def get_club_id(student_id):
    sql = "SELECT club_id FROM student_club WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (student_id,))
    club_id = cursor.fetchone()
    cursor.close()
    connection.close()
    return club_id
    
#　入力された内容を保存する。
@club_edit_bp.route('/club_edit_input', methods=['POST'])
def club_edit_input():
    club_name = request.form.get('club_name')
    mail = request.form.get('mail')
    objective = request.form.get('objective')
    activites = request.form.get('activites')
    introduction = request.form.get('introduction')
    note = request.form.get('note')
    return render_template("club_edit_conf.html", club_name = club_name, mail = mail, objective = objective, activites = activites, introduction = introduction, note = note)

#　入力された内容をclub_changeテーブルにinsertする。
@club_edit_bp.route('/club_edit_conf' , methods = ['POST'])
def club_edit_conf():
    club_id = session.get("club_id")
    club_name = request.form.get('club_name')
    mail = request.form.get('mail')
    objective = request.form.get('objective')
    activites = request.form.get('activites')
    introduction = request.form.get('introduction')
    note = request.form.get('note')
    student_id = get_student_id(mail)
    insert_club_change(club_id, club_name, student_id, objective, activites, introduction, note)
    return render_template("club_edit_res.html")

def get_student_id(mail):
    sql = "SELECT student_id FROM student WHERE mail = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (mail,))
    studnet_id = cursor.fetchone()
    cursor.close()
    connection.close()
    return studnet_id


def insert_club_change(club_id, club_name, student_id, objective, activites, introduction, note):
    sql = "INSERT INTO club_change (club_id, name, leader_id, objective, activities, introduction, note)VALUES(%s, %s, %s, %s, %s, %s, %s)"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id, club_name, student_id, objective, activites, introduction, note))
    connection.commit()
    print('ok')
    connection.close()
    cursor.close()
    
#<------------------------------------------------------------------->

#管理者による変更申請の承認処理
#申請一覧の表示
@club_edit_bp.route('/club_edit_reqlist')
def club_edit_reqlist():
    club_list = get_leader_id()
    return render_template('club_req_list.html' ,club_list = club_list)
    
#leader_idの取得
def get_leader_id():
    sql = "SELECT * FROM club_change "
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql)
    club_list = []
    for row in cursor.fetchall():
        leader_name = get_leader(row[2])
        year = get_leader(row[2])
        department = get_department(row[2])
        club_list.append((row[0], row[1], leader_name[1], department[1], year[4])) #row[0]=club_id, row[1]=club_name
    cursor.close()
    connection.close()
    return club_list
    
    #reader_idからリーダーの情報を取得
def get_leader(student_id):
    sql = "SELEcT * FROM student WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (student_id,))
    leader = cursor.fetchone()
    cursor.close()
    connection.close()
    return leader


#department_idからdepartment_name取得
def get_department(department_id):
    sql = "SELECT * FROM department WHERE department_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (department_id,))
    department = cursor.fetchone()
    cursor.close()
    connection.close()
    return department

@club_edit_bp.route('/disp_edit_req')
def disp_edit_req():
    club_id = request.args.get("club_id")
    session["club_id"] = club_id
    #サークル名を取得する
    club_name = list(filter(lambda t: t != ('',), get_club_name(club_id)))
    print(club_name)
    
    #リーダーのstudent_idを取得する
    student_id= get_student_id2(club_id)
    print(student_id)
    
    #リーダーのメールアドレスを取得する
    mail = list(filter(lambda t: t != ('',),get_leader_mail(student_id)))
    print(mail)
    
    #活動目標を取得する
    objective =list(filter(lambda t: t != ('',),get_objective(club_id)))
    print(objective)
    
    #活動内容を取得する
    activities =list(filter(lambda t: t != ('',),get_activities(club_id)))
    print(activities)
    
    #サークルの説明を取得する
    introduction =list(filter(lambda t: t != ('',),get_introduction(club_id)))
    print(introduction)
    
    #備考を取得する
    note =list(filter(lambda t: t != ('',),get_note(club_id)))
    print(note)
    
    return render_template('disp_edit_req.html' ,
                           club_name = club_name, mail = mail, objective = objective, activities = activities, introduction = introduction, note = note)

def get_club_name(club_id):
    sql = "SELECT name FROM club_change WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    club_name = cursor.fetchone()
    cursor.close()
    connection.close()
    return club_name

def get_student_id2(club_id):
    sql = "SELECT leader_id FROM club_change WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    student_id = cursor.fetchone()
    cursor.close()
    connection.close()
    return student_id

def get_leader_mail(student_id):
    sql = "SELECT mail FROM student WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (student_id,))
    mail = cursor.fetchone()
    cursor.close()
    connection.close()
    return mail

def get_objective(club_id):
    sql = "SELECT objective FROM club_change WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    objective = cursor.fetchone()
    cursor.close()
    connection.close()
    return objective

def get_activities(club_id):
    sql = "SELECT activities FROM club_change WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    activities = cursor.fetchone()
    cursor.close()
    connection.close()
    return activities

def get_introduction(club_id):
    sql = "SELECT introduction FROM club_change WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    introduction = cursor.fetchone()
    cursor.close()
    connection.close()
    return introduction

def get_note(club_id):
    sql = "SELECT note FROM club_change WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    note = cursor.fetchone()
    cursor.close()
    connection.close()
    return note

#承認ボタンを押した時の処理
@club_edit_bp.route('/club_edit_reqok', methods=['POST'])
def club_edit_reqok():
    club_id = session.get("club_id")
    club_name = request.form.get("club_name")
    mail = request.args.get("mail")
    objective = request.args.get("objective")
    activities = request.args.get("activities")
    note = request.args.get("note")
    student_id= get_student_id2(club_id)
    print(club_name)
    
    #student_clubのis_leaderをfalseにする
    leader_false(club_id)
    
    #clubテーブルのデータを変更する
    update_club(club_name, mail, objective, activities, note, club_id)
    
    #student_clubのis_leaderをtrueにする
    leader_true(student_id)
    
    #club_changeテーブルのデータを削除する。
    delete_change(club_id)
    return render_template('club_editreq_ok.html')

def leader_false(club_id):
    sql = "UPDATE student_club SET is_leader = 'f' WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()   
    cursor.execute(sql, (club_id,))
    connection.commit()
    cursor.close()
    connection.close()  

def update_club(club_name, mail, objective, activities, note, club_id ):
    sql = "UPDATE club SET name = %s, mail = %s, objective = %s, activities = %s, note = %s, allow = 2 WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()   
    cursor.execute(sql, (club_name, mail, objective, activities, note, club_id))
    connection.commit()
    cursor.close()
    connection.close()
    
def leader_true(student_id):
    sql = "UPDATE student_club SET is_leader = 't' WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()   
    cursor.execute(sql, (student_id,))
    connection.commit()
    cursor.close()
    connection.close() 
    
def delete_change(club_id):
    sql = "DELETE FROM club_change WHERE club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()   
    cursor.execute(sql, (club_id,))
    connection.commit()
    cursor.close()
    connection.close() 
