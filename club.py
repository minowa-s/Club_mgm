from flask import Blueprint, render_template, request, session
import hashlib, string, random, psycopg2, os, bcrypt, datetime, smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

club_bp = Blueprint('club', __name__, url_prefix='/club')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

#サークル参加申請処理
@club_bp.route("/club_join_req", methods=["POST"])
def club_join_req():
    student_id = request.form.get("student_id")
    session["student_id"] = student_id
    print(student_id)
    return render_template("club_join.html" ,student_id = student_id)

@club_bp.route("/club_join_req2", methods=["POST"])
def club_join_req2():
    student_id = session.get("student_id")
    print(student_id)
    return render_template("club_join_send.html" ,student_id = student_id)

#サークル参加申請確認処理
@club_bp.route("/club_join_req3", methods=["GET", "POST"])
def club_join_req3():
    student_id = session.get("student_id")
    club_id = request.form.get("club_id")
    print(student_id)
    sql = "INSERT INTO student_club (student_id, club_id, is_leader, allow) VALUES (%s, %s, %s, %s)"

    try :
        connection = get_connection()
        cursor = connection.cursor()   
        cursor.execute(sql, (student_id, club_id, False, 0))
        connection.commit()
        
    except psycopg2.DatabaseError:
            count = 0
            
    finally :
            cursor.close()
            connection.close()
            
    return render_template('club_join_reqres.html')

