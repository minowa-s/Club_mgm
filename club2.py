from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib, db, app_data
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

club_bp2 = Blueprint('club2', __name__, url_prefix='/club2')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

#参加申請一覧機能
@club_bp2.route("/join_req_list")
def join_req_list():
    id = request.args.get("student") #リーダーのid
    club_id = db.get_club_id(id) #リーダー情報からclub_id取得 
    student = db.get_student(id) #リーダーのstudent情報
    list = get_list(club_id) #club_idを使ってそのサークルに来ている申請を取得
    if not list:  # もしくは if len(my_list) == 0:
        return render_template("leader/0request_list.html", student=student)
    else:
        return render_template("leader/request_list.html" ,list = list, student=student)
 
def get_list(club_id):
    sql = "SELECT * FROM student_club WHERE allow = 0 and club_id = %s"
    
    try :
        connection = get_connection()
        cursor = connection.cursor()   
        cursor.execute(sql, (club_id,))
        connection.commit()
        
    except psycopg2.DatabaseError:
        count = 0
    
    result_list = []  # list を変数名と重複しないように変更
    for row in cursor.fetchall():
        name = get_name(row[1])
        student = db.get_student(row[1])
        entrance_year = student[4]
        department_name = app_data.get_department(student[5])
        request_student = db.get_student(row[1])
        result_list.append((request_student[2], name, entrance_year,  department_name, student[0]))  # name を追加
    cursor.close()
    connection.close()
    return result_list

# -------------------------------------------------------
#サークル参加申請承認
@club_bp2.route("/join_req", methods=['POST'])
def join_req():
    approve = request.form.get("approve")
    print(approve)
    student = request.form.get("student_id")
    if approve == "1" :
        return join_req_ok(student)
    else :
        return join_req_no(student)
    
#申請承認機能
#一覧からidを取得して次の画面に遷移させる処理
def join_req_ok(student_id):
    return render_template("join_reqest/join_req_okexe.html" ,student = student_id)

#下に書いてあるsqlを実行し完了画面に遷移させる処理
@club_bp2.route("/join_req_okexe", methods=["POST"] )
def join_req_okexe():
    student_id = request.form.get("student_id")
    student = db.get_student(student_id)
    print(student)
    db.mail_send(student[2], "参加申請について", "参加申請が承認されました")
    join_ok_sql(student_id)
    return render_template("join_reqest/join_req_okres.html", student=student_id)

#student_idを元にallowを変更するUPDATE文
def join_ok_sql(student_id):
    sql = "UPDATE student_club SET allow = 1 WHERE student_id = %s" 
    connection = get_connection()
    cursor = connection.cursor()   
    cursor.execute(sql, (student_id,))
    connection.commit()
    cursor.close()
    connection.close()

# ------------------------------------------------------
#申請否認機能
def join_req_no(student_id):
    session["student_id"] = student_id
    return render_template("join_reqest/join_req_noexe.html", student = student_id)

#否認理由の取得
@club_bp2.route('/join_req_noexe',methods=['POST'])
def join_req_noexe():
    reason  = request.form.get("reason")
    student_id = request.form.get("student_id")
    print(reason)
    return render_template("join_reqest/join_req_noconf.html", reason=reason, student=student_id)

#セッションからstudent_idを持ってきてそれを引数にUPDATEを実行
@club_bp2.route('/join_req_noconf', methods=['POST'])
def join_req_noconf():
    reason = request.form.get("reason")
    student_id = session.get("student_id")
    student = db.get_student(student_id)
    db.mail_send(student[2], "参加申請について", reason)
    join_no_sql(student_id)
    return render_template("join_reqest/join_req_nores.html", student=student_id)

#student_idを元にallowを変更するUPDATE文
def join_no_sql(student_id):
    sql = "UPDATE student_club SET allow = 2 WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()   
    cursor.execute(sql, (student_id,))
    connection.commit()
    cursor.close()
    connection.close()


#student_idから学生氏名取得  
def get_name(id):
    sql = "SELECT name FROM student WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()   
    cursor.execute(sql, (id,))
    name_list = [row[0] for row in cursor.fetchall()]  # row[0] のみ取得
    cursor.close()
    connection.close()
    return name_list
    
#----------------------------------------------------------------------
#サークル削除申請
@club_bp2.route("/club_delete_request")
def club_delete_request():
    return render_template('join_reqest/club_delete_request.html')

@club_bp2.route('/club_delete_request_exe')
def club_delete_request_exe():
    #sessionかrequestか知らないけどclub_idとってくる
    club_id = 1
    db.delete_club(club_id)
    return render_template("join_reqest/club_delete_request_exe.html")