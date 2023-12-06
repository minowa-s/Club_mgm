from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
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
    list = get_list()
    return render_template("join_req_list.html" ,list = list)
    
def get_name(id):
    sql = "SELECT name FROM student WHERE student_id = %s"
     
    connection = get_connection()
    cursor = connection.cursor()   
    cursor.execute(sql, (id,))
    name_list = [row[0] for row in cursor.fetchall()]  # row[0] のみ取得
    cursor.close()
    connection.close()

    return name_list

    
def get_list():
    sql = "SELECT * FROM student_club WHERE allow = 0"
    
    try :
        connection = get_connection()
        cursor = connection.cursor()   
        cursor.execute(sql )
        connection.commit()
        
    except psycopg2.DatabaseError:
        count = 0
    
    name = get_name(1)
    result_list = []  # list を変数名と重複しないように変更
    for row in cursor.fetchall():
        result_list.append((row[0], row[1], name))  # name を追加
    cursor.close()
    connection.close()
    return result_list

# -------------------------------------------------------
#申請承認機能
#一覧からidを取得して次の画面に遷移させる処理
@club_bp2.route("/join_req_ok")
def join_req_ok():
    student_id = request.args.get("student_id")
    return render_template("join_req_okexe.html" ,student_id = student_id)

#下に書いてあるsqlを実行し完了画面に遷移させる処理
@club_bp2.route("/join_req_okexe", methods=["POST"] )
def join_req_okexe():
    student_id = request.form.get("student_id")
    join_ok_sql(student_id)
    return render_template("join_req_okres.html")

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
@club_bp2.route('/join_req_no')
def join_req_no():
    student_id = request.args.get("student_id")
    session["student_id"] = student_id
    return render_template("join_req_noexe.html", student_id = student_id)

#否認理由の取得
@club_bp2.route('/join_req_noexe')
def join_req_noexe():
    reason  = request.args.get("reason")
    return render_template("join_req_noconf.html", reason = reason)

#セッションからstudent_idを持ってきてそれを引数にUPDATEを実行
@club_bp2.route('/join_req_noconf')
def join_req_noconf():
    reason = request.form.get("reason")
    student_id = session.get("student_id")
    join_no_sql(student_id)
    return render_template("join_req_nores.html")

#student_idを元にallowを変更するUPDATE文
def join_no_sql(student_id):
    sql = "UPDATE student_club SET allow = 2 WHERE student_id = %s"
    connection = get_connection()
    cursor = connection.cursor()   
    cursor.execute(sql, (student_id,))
    connection.commit()
    cursor.close()
    connection.close()


    
    
    