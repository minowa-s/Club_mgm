from flask import Blueprint,  render_template, request, session, url_for
import psycopg2, db, os, app_data
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication

leader_bp = Blueprint('leader', __name__, url_prefix='/leader')

#DB接続
def get_connection():
    url = os.environ['DATABASE_URL']
    connection = psycopg2.connect(url)
    return connection

@leader_bp.route("/requst_list")
def request_list():
    mail = session.get('mail')
    #student_id取得
    id = db.get_id(mail)
    club_id = db.get_club_id(id)
    print(club_id)
    request_list = get_request(club_id)
    print("requ==", request_list)
    if request_list:
        student = db.get_student(request_list[0][1])
        department = app_data.get_department(student[5])
        department = department[1]
    else:
        # request_list が空の場合の処理
        student = None
        department = None
        return render_template('leader/0request_list.html')
    return render_template('leader/request_list.html', student=student, department=department)

def get_request(club_id):
    sql = "SELECT * FROM student_club WHERE allow = 0 and club_id = %s"
    connection = get_connection()
    cursor = connection.cursor()
    cursor.execute(sql, (club_id,))
    list = cursor.fetchall()
    cursor.close()
    connection.close()
    return list